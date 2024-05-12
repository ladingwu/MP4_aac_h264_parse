# This is a sample Python script.
from h264Data import H264Reader

from AacData import ADTSHeader
from Mp4Data import *


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def print_AAC(file_name):
    with open(file_name, 'rb') as file:
        ADTSHeader().printSelf(file)


        print("\n======================= read end ==============================")
def print_MP4(file_name):

    #print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    with open(file_name, 'rb') as file:
        box_type, box_size = Box().findBoxHeader(file)
        while True:

            #print("current type {0}".format(box_type))
            if box_type == 'ftyp':
                box_type, box_size = FtypBox(box_type,box_size).printSelf(file)

            elif box_type == 'moov':
                box_type, box_size = MoovBox(box_type,box_size).printSelf(file)

            else:
                break

            if box_type is None and box_size is None:
                box_type, box_size = Box().findBoxHeader(file)

        print("\n======================= read end ==============================")

def print_h264(file_name):
    with open(file_name, 'rb') as file:
        H264Reader().printSelf(file)

        print("\n======================= read end ==============================")


if __name__ == '__main__':
    # print_MP4('sample.mp4')
    print_h264('sample.264')
