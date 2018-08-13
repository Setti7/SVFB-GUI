# Citation: Box Of Hats (https://github.com/Box-Of-Hats )

import win32api as wapi

# keyList = ["\b"]
# for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'£$/\\":
#     keyList.append(char)
#
#
# def key_check():
#     keys = []
#     for key in keyList:
#         if wapi.GetAsyncKeyState(ord(key)):
#             keys.append(key)
#     return keys


def key_check(key):
    if wapi.GetAsyncKeyState(ord(key)):
        return 1
    else:
        return 0