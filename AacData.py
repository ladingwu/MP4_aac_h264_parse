class ADTSHeader(object):
    one_byte = 1
    two_byte = 2
    three_byte = 3

    def getProfile(self,profile):
        profile_real = 'reserved'
        if profile == 1:
            profile_real = 'Low Complexity profile (LC) '
        elif profile == 2:
            profile_real = 'Scalable Sampling Rate profile (SSR)'
        elif profile == 0:
            profile_real = 'Main Profile'

        return profile_real


    def getLayer(self,layer):
        layer_real = 'reserved'
        if layer == 1:
            layer_real = 'Layer III'
        elif layer == 2:
            layer_real = 'Layer II'
        elif layer == 3:
            layer_real = 'Layer I'

        return layer_real

    def getChannelConfiguration(self,chanel):
        channel_configure = str(chanel)
        if chanel == 6:
            channel_configure = '5+1'
        elif chanel == 7:
            channel_configure = '7+1'


        return channel_configure



    def getSampling(self,sampling_frequency):
        sampling_frequency_value = '0'
        if sampling_frequency == 0:
            sampling_frequency_value = '96khz'
        elif sampling_frequency == 1:
            sampling_frequency_value = '88.2khz'
        elif sampling_frequency == 2:
            sampling_frequency_value = '64khz'
        elif sampling_frequency == 3:
            sampling_frequency_value = '48khz'
        elif sampling_frequency == 4:
            sampling_frequency_value = '44.1khz'
        elif sampling_frequency == 5:
            sampling_frequency_value = '32khz'
        elif sampling_frequency == 6:
            sampling_frequency_value = '24khz'
        elif sampling_frequency == 7:
            sampling_frequency_value = '22khz'
        elif sampling_frequency == 8:
            sampling_frequency_value = '16khz'
        elif sampling_frequency == 9:
            sampling_frequency_value = '12khz'
        elif sampling_frequency == 10:
            sampling_frequency_value = '11.025khz'
        elif sampling_frequency == 10:
            sampling_frequency_value = '0.8khz'
        else:
            sampling_frequency_value = 'reserved'

        return sampling_frequency_value

    def printSelf(self,file):
        result = int.from_bytes(file.read(self.two_byte))
        syncword = result >> 4
        id = (result & 0x0008) >> 3
        layer = (result & 0x0006) >> 1
        protection_absent = (result & 0x0001)

        result = int.from_bytes(file.read(self.two_byte))
        profile = result >> 14
        sampling_frequency_index = (result & 0x3c00) >> 10
        private_bit = (result & 0x0200) >> 9
        channel_configuration = (result & 0x01c0) >> 6
        original_copy = (result & 0x0020) >> 5
        home = (result & 0x0010) >> 4

        # 以下是可变头部的数据读取
        copyright_identification_bit = (result & 0x0008) >> 3
        copyright_identification_start = (result & 0x0004) >> 2
        remain_2 = (result & 0x3) # 剩余2bit

        result = int.from_bytes(file.read(self.three_byte)) #读取剩余3byte

        aac_frame_length = (result >> 13) | (remain_2 << 11)

        adts_buffer_fullness = (result & 0x1ffc) >> 2
        number_of_raw_data_blocks_in_frame = (result & 0x3)

        print("================================= adts_fixed_header ==========================")
        print("syncword: {0}".format(hex(syncword)))
        print("id: {0}".format(id))
        print("layer: {0} : {1}".format(layer,self.getLayer(layer)))
        print("protection_absent: {0}".format(protection_absent))
        print("profile:  {0} ".format(self.getProfile(profile)))
        print("sampling_frequency_index:  {0} ".format(self.getSampling(sampling_frequency_index)))
        print("private_bit: {0}".format(private_bit))
        print("channel_configuration: {0} ".format(self.getChannelConfiguration(channel_configuration)))
        print("original_copy: {0}".format(original_copy))
        print("home: {0}".format(home))


        print("================================= adts_variable_header ==========================")
        print("copyright_identification_bit: {0}".format(copyright_identification_bit))
        print("copyright_identification_start: {0}".format(copyright_identification_start))
        print("aac_frame_length: {0}".format(aac_frame_length))
        print("adts_buffer_fullness: {0}".format(hex(adts_buffer_fullness)))
        print("number_of_raw_data_blocks_in_frame: {0}".format(number_of_raw_data_blocks_in_frame))