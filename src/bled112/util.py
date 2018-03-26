#!/usr/bin/env/python
# -*- coding: utf-8 -*-

import array
import zlib
import glob
import time


def get_byte_packet(packetno, frameno, databytes):
    '''
    Returns a subarray that fits into a bluetooth packet
    '''
    subarray = databytes[frameno][packetno * 22:(packetno + 1) * 22]  # is empty as soon as we request more
    return subarray


def get_char_array(text_blob):
    '''
    Returns an array of unsigned chars given a string
    '''
    return array.array("B", text_blob)


def compress(text_blob):
    '''
    Returns a compressed string using zlib at the moment
    '''
    return zlib.compress(text_blob, 9)


def pad_truncate(text_blob, length):
    '''
    Returns a string of exactly length characters, padding or truncating adequately
    '''
    format_string = '{:.' + str(length) + '}'
    text_blob = format_string.format(text_blob)  # cut down to lenght char
    # text_blob = "{:<10}".format(text_blob) # fill up with whitespace to 8 char
    return text_blob


def get_tty_paths():
    res = [f for f in glob.glob('/dev/tty.usb*') + glob.glob('/dev/ttyACM*') +
           glob.glob('/dev/ttyU*') if "init" not in f and "lock" not in f and
           "ACM0" not in f and "ACM1" not in f and "ACM2" not in f]
    return res


def current_milli_time():
    return int(round(time.time() * 1000))
