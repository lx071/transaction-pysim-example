import os
# import random
import subprocess
import re


def send_data():
    data_package = 0
    # 3bytes * 100 = 300bytes = 2400bit 

    for j in range(100):
        data_item = j % 200
        op_item = 1
        data_package = (data_package << 24) + (data_item << 16) + (data_item << 8) + op_item
        pass
    bytes_val = data_package.to_bytes(300, 'little')
    return bytes_val
    pass


if __name__ == '__main__':
    pass
