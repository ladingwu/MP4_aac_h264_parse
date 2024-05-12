class Box(object):
    # 通用的4字节
    one_bytes = 1
    two_bytes = 2
    three_bytes = 3
    four_bytes = 4
    eight_bytes = 8

    # 当前box的大小
    box_size = 0
    box_header_size = 8
    box_type = ''
    # fullbox 的version字段 int
    box_version = 0
    # 当前box是否是 FullBox
    isFullBox = False

    header_read_already = False

    def __init__(self, box_type=None, size=None):
        self.box_size = size
        self.box_type = box_type
        if box_type is not None and size is not None:
            self.header_read_already = True

    def findBoxHeader(self, file):
        self.box_size = int.from_bytes(file.read(self.four_bytes))
        self.box_type = file.read(self.four_bytes).decode()
        return self.box_type, self.box_size

    def print_origin_for_test(self, file):
        if not self.header_read_already:
            self.findBoxHeader(file)
        last = file.read(self.box_size - self.four_bytes)
        print("{0} box,size:{1} last byte:{2}".format(self.box_type, self.box_size, last))

    def printSelf(self, file):
        if not self.header_read_already:
            self.findBoxHeader(file)
        print(
            "\n============================================== {0} box ==========================================".format(
                self.box_type))
        print("type:{0}  ".format( self.box_type))
        print("size:{0}  ".format( self.box_size))
        if self.box_size == 1:
            box_large_size = file.read(self.eight_bytes)
            print("large_size:{0}  ".format(box_large_size))
            self.box_header_size = self.box_header_size + 8
        if self.isFullBox:
            box_version = int.from_bytes(file.read(self.one_bytes))
            box_flags = int.from_bytes(file.read(self.three_bytes))
            print("box_version:{0}  ".format(box_version))
            print("box_flags:{0}  ".format(box_flags))
            self.box_header_size = self.box_header_size + 4

        # 是否读取了下一个box的头部信息，读了的话要返回回去
        return None,None

class FtypBox(Box):
    used_bytes = 16

    def printSelf(self, file):
        super().printSelf(file)

        minor_brand = file.read(self.four_bytes).decode()
        minor_version = int.from_bytes(file.read(self.four_bytes))
        last_size = self.box_size - self.used_bytes
        index = 0
        compatible_brand = []
        while index < last_size:
            count = 4
            compatible_brand_item = file.read(count).decode()
            compatible_brand.append(compatible_brand_item)
            index = index + count

        print("minor_brand:{0}  ".format(minor_brand))
        print("minor_version:{0}  ".format(minor_version))
        print("compatible_brand:{0}  ".format(str(compatible_brand)))
        return None,None

class MoovBox(Box):
    def printSelf(self, file):
        super().printSelf(file)
        type, size = Box().findBoxHeader(file)

        while type=='mvhd' or type == 'trak':
            if type == 'mvhd':
                mvhd_box = MvhdBox(type,size)
                type, size = mvhd_box.printSelf(file)

            elif type == 'trak':
                trak_box = TrakBox(type,size)
                type, size = trak_box.printSelf(file)

            if type is None and size is None:
                type, size = Box().findBoxHeader(file)
        return type,size;

class MvhdBox(Box):

    def __init__(self, box_type=None, size=None):
        self.isFullBox = True
        super().__init__(box_type, size)

    def printSelf(self, file):
        super().printSelf(file)
        if self.box_version == 1:
            creation_time = int.from_bytes(file.read(self.eight_bytes))
            modification_time = int.from_bytes(file.read(self.eight_bytes))
            timescale = int.from_bytes(file.read(self.four_bytes))
            duration = int.from_bytes(file.read(self.eight_bytes))
        else:
            creation_time = int.from_bytes(file.read(self.four_bytes))
            modification_time = int.from_bytes(file.read(self.four_bytes))
            timescale = int.from_bytes(file.read(self.four_bytes))
            duration = int.from_bytes(file.read(self.four_bytes))
        rate_all = int.from_bytes(file.read(self.four_bytes))
        rate_f = rate_all & 0xffff
        rate_i = rate_all >> 16

        volume_all = int.from_bytes(file.read(self.two_bytes))
        volume_f = volume_all & 0xff
        volume_i = volume_all >> 8

        reserved = file.read(self.two_bytes)

        reserved_1 = file.read(self.four_bytes)
        reserved_2 = file.read(self.four_bytes)
        matrix = []
        for i in range(9):
            matrix.append(int.from_bytes(file.read(self.four_bytes)))

        pre_define = []
        for i in range(6):
            pre_define.append(int.from_bytes(file.read(self.four_bytes)))

        next_track_ID = int.from_bytes(file.read(self.four_bytes))

        print("creation_time:{0}  ".format(creation_time))
        print("modification_time:{0}  ".format(modification_time))
        print("timescale:{0}  ".format(timescale))
        print("duration:{0}  ".format(duration))
        print("rate:{0}.{1}  ".format(rate_i, rate_f))
        print("volume:{0}.{1}  ".format(volume_i, volume_f))
        print("reserved:{0}  ".format(reserved))
        print("reserved[] :{0} , {1} ".format(reserved_1, reserved_2))
        print("matrix:{0}  ".format(matrix))
        print("pre_define:{0}  ".format(pre_define))
        print("next_track_ID:{0}  ".format(next_track_ID))
        return None,None


class TrakBox(Box):
    def printSelf(self, file):
        super().printSelf(file)
        #获取内部的下一个box
        type,size = Box().findBoxHeader(file)
        index = 0
        while type == 'tkhd' :
            tkhd_box = TkhdBox(type,size)
            type, size = tkhd_box.printSelf(file)
            print("\n{0} box remain size======> {1}".format(tkhd_box.box_type,(self.box_size-tkhd_box.box_size)))
            # box剩余的还没读取数据一次性计提
            tkhd_remain_size = file.read(self.box_size-tkhd_box.box_size)

            if type is None and size is None:
                type, size = Box().findBoxHeader(file) #读取下一个box的头部信息

        return type,size #下一个box的头部信息



class TkhdBox(Box):

    def __init__(self, box_type=None, size=None):
        self.isFullBox = True
        super().__init__(box_type, size)

    def printSelf(self, file):
        super().printSelf(file)
        if self.box_version == 1:
            creation_time = int.from_bytes(file.read(self.eight_bytes))
            modification_time = int.from_bytes(file.read(self.eight_bytes))
            track_ID = int.from_bytes(file.read(self.four_bytes))
            reserved_32 = int.from_bytes(file.read(self.four_bytes))
            duration = int.from_bytes(file.read(self.eight_bytes))
        else:
            creation_time = int.from_bytes(file.read(self.four_bytes))
            modification_time = int.from_bytes(file.read(self.four_bytes))
            track_ID = int.from_bytes(file.read(self.four_bytes))
            reserved_32 = int.from_bytes(file.read(self.four_bytes))
            duration = int.from_bytes(file.read(self.four_bytes))

        reserved_1 = int.from_bytes(file.read(self.four_bytes))
        reserved_2 = int.from_bytes(file.read(self.four_bytes))


        layer  = int.from_bytes(file.read(self.two_bytes))
        alternate_group = int.from_bytes(file.read(self.two_bytes))
        volume_all = int.from_bytes(file.read(self.two_bytes))
        volume_f = volume_all & 0xff
        volume_i = volume_all >> 8
        reserved_16 = int.from_bytes(file.read(self.two_bytes))

        matrix = []
        for i in range(9):
            matrix.append(int.from_bytes(file.read(self.four_bytes)))

        width = int.from_bytes(file.read(self.four_bytes)) >> 16
        height = int.from_bytes(file.read(self.four_bytes)) >> 16

        print("creation_time:{0}  ".format(creation_time))
        print("modification_time:{0}  ".format(modification_time))
        print("track_ID:{0}  ".format(track_ID))
        print("reserved_32:{0}  ".format(reserved_32))
        print("duration:{0}  ".format(duration))
        print("duration:{0}  ".format(duration))
        print("reserved[]:{0} {1}  ".format(reserved_1,reserved_2))
        print("layer:{0}  ".format(layer))
        print("alternate_group:{0}  ".format(alternate_group))
        print("volume:{0}.{1}  ".format(volume_i,volume_f))
        print("reserved_16:{0}  ".format(reserved_16))
        print("matrix:{0}  ".format(matrix))
        print("width:{0}  ".format(width))
        print("height:{0}  ".format(height))

        return None, None
