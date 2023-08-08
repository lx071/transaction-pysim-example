import os
# import random
import subprocess
import re


def send_data():
    data_package = 0
    # 2bytes * 100 = 200bytes = 1600bit 
    for j in range(100):
        data_item = j % 200
        data_package = (data_package << 16) + (data_item << 8) + data_item
        pass

    bytes_val = data_package.to_bytes(200, 'little')
    return bytes_val
    pass


if __name__ == '__main__':
    pass
