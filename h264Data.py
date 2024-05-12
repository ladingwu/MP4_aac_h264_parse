class NALU(object):
    forbidden_zero_bit = -1
    nal_ref_idc = -1
    nal_unit_type = -1
    nal_unit_type_str = ''
    start_in_file = -1
    end_in_file = -1
    size = -1

    def copy_from(self,nalu_obj):
        self.forbidden_zero_bit = nalu_obj.forbidden_zero_bit
        self.nal_ref_idc = nalu_obj.nal_ref_idc
        self.nal_unit_type = nalu_obj.nal_unit_type
        self.nal_unit_type_str = nalu_obj.nal_unit_type_str
        self.start_in_file = nalu_obj.start_in_file
        self.end_in_file = nalu_obj.end_in_file
        self.size = nalu_obj.size

    def to_string(self):
        print("========================{0} NALU Header=============================".format(self.nal_unit_type_str))
        print("forbidden_zero_bit:{0}".format(self.forbidden_zero_bit))
        print("nal_ref_idc:{0}".format(self.nal_ref_idc))
        print("nal_unit_type:{0} {1}".format(self.nal_unit_type,self.nal_unit_type_str))
        print("nalu size: {0}".format(self.size))
        print("in file start:{0}".format(self.start_in_file))
        print("in file end:{0}".format(self.end_in_file))

    def parse_data(self,file):
        pass

class IDRSliceNALU(NALU):
    def __init__(self,nalu_obj):
        super().copy_from(nalu_obj)

    def parse_data(self,file):
        file.seek(0,self.start_in_file)






class NaluDataFinder(object):
    BYTE_ONE = 1
    BYTE_TWO = 2
    BYTE_THREE = 3
    BYTE_FOUR = 4
    BYTE_10M = 10*1024*1024

    def isStartCode(self,file):
        data_byte = file.read(self.BYTE_THREE)
        if len(data_byte) < self.BYTE_THREE: # 没读到预期值表明已经读到结尾了
            #print("数据不足 {0}，已经读到文件末尾了".format(len(data_byte)))
            return False ,len(data_byte)
        data =  int.from_bytes(data_byte)
        if not data_byte:
            return False,0
        #print(hex(data))
        byte_num = 3
        if data == 0x000001:
            #print("start code 0x000001")
            return True,byte_num
        if data == 0x000000:
            end = int.from_bytes(file.read(self.BYTE_ONE))
            if not end:
                return False,byte_num
            byte_num = byte_num+1
            data = (data << 8) | end
            if end == 0x01:
                #print("start code 0x00000001  ===== ")

                return True, byte_num

        #print("start code not found !!!")
        return False,byte_num
    def getNALUType(self,nalu_type):
        if nalu_type == 0:
            return "unspecified"
        elif nalu_type == 1:
            return "non-IDR slice layer"
        elif nalu_type == 2 or nalu_type == 3 or nalu_type == 4:
            return "A/B/C slice data"
        elif nalu_type == 5:
            return "IDR slice layer"
        elif nalu_type == 6:
            return "SEI"
        elif nalu_type == 7:
            return "SPS"
        elif nalu_type == 8:
            return "PPS"
        elif nalu_type == 9:
            return "unit-delimiter"
        else:
            return "other-type"
    def printSelf(self,file,start_index):
        isEnd = False
        nalu_size = 1 #当前的nalu的大小
        one_byte_data = file.read(self.BYTE_ONE)
        nalu_obj = NALU()
        # if not one_byte_data:
        #     #print("read file eof +++")
        #     isEnd = True
        #     return isEnd,0
        byte_data = int.from_bytes(one_byte_data)

        forbidden_zero_bit = byte_data >> 7
        nal_ref_idc = (byte_data & 0x70) >> 5
        nal_unit_type = (byte_data & 0x1f)

        nalu_obj.forbidden_zero_bit = forbidden_zero_bit
        nalu_obj.nal_ref_idc = nal_ref_idc
        nalu_obj.nal_unit_type = nal_unit_type
        nalu_obj.nal_unit_type_str = self.getNALUType(nal_unit_type)
        nalu_obj.start_in_file = start_index

        # print("========================{0} NALU =============================".format(self.getNALUType(nal_unit_type)))
        # print("forbidden_zero_bit:{0}".format(forbidden_zero_bit))
        # print("nal_ref_idc:{0}".format(nalu_obj.nal_ref_idc))
        # print("nal_unit_type:{0} {1}".format(nalu_obj.nal_unit_type,nalu_obj.nal_unit_type_str))

        is_start_code, read_byte_num =self.isStartCode(file)
        while not is_start_code and read_byte_num >= 3:
            nalu_size = nalu_size+1;
            seek_num = 0-(read_byte_num-1)
            file.seek(seek_num,1)
            is_start_code, read_byte_num = self.isStartCode(file)

        if not is_start_code and read_byte_num < 3:
            nalu_size = nalu_size+read_byte_num

        nalu_obj.end_in_file = start_index+nalu_size
        nalu_obj.size = nalu_size
        # print("nalu size: {0}  in file start:{1} end:{2}".format(nalu_size,nalu_obj.start_in_file,nalu_obj.end_in_file))
        next_start = start_index + nalu_size + read_byte_num
        if read_byte_num < 3:
            print("read file eof ===")
            isEnd = True
            return isEnd,next_start,nalu_obj

        return isEnd,next_start,nalu_obj



class H264Reader(object):
    def printSelf(self,file):
        nalu_finder =  NaluDataFinder()
        is_start_code,read_byte_num = nalu_finder.isStartCode(file)
        isEnd = False
        if read_byte_num == 0: # 读取完毕
            #print("read file eof ----")
            isEnd = True
            return isEnd

        start_index = read_byte_num
        nalu_array = [] # 存储NALU列表
        end,start_index,nalu_obj = nalu_finder.printSelf(file,start_index)
        nalu_array.append(nalu_obj)
        while not end:
            end,start_index,nalu_obj = nalu_finder.printSelf(file,start_index)
            nalu_array.append(nalu_obj)


        # for item in nalu_array:
        #     item.to_string()







