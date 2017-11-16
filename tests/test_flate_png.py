#! /usr/bin/env python
# encoding: utf-8
# A part of pdfrw (https://github.com/pmaupin/pdfrw)
# Copyright (C) 2006-2017 Patrick Maupin, Austin, Texas
#                    2017 Henddher Pedroza, Illinois
# MIT license -- See LICENSE.txt for details

'''
Run from the directory above like so:
python -m tests.test_pdfstring
'''


from pdfrw.uncompress import flate_png, flate_png_orig, flate_png_impl
from pdfrw.py23_diffs import zlib, xrange, from_array, convert_load, convert_store

import unittest
import base64
import array
import logging
import ast
import os

#
# Sample PNGs with filtered scanlines retrieved from
# http://www.schaik.com/pngsuite/pngsuite_fil_png.html
#

def filepath(filename):
    pwd = os.path.dirname(__file__)
    return os.path.join(pwd, filename)

def create_data(nc=1, nr=1, bpc=8, ncolors=1, filter_type=0):
    pixel_size = (bpc * ncolors + 7) // 8
    data = []
    for r in xrange(nr):
        data.append(filter_type if r > 0 else 0) # filter byte
        for c in xrange(nc * pixel_size):
            data.append(r * nc * pixel_size + c * pixel_size)
    data = array.array('B', data)
    logging.debug("Data: %r" % (data))
    return data, nc, nr, bpc, ncolors

def prepend_data_with_filter(data, filter):
    a = array.array('B', data)
    a.insert(0, filter)
    return a

def print_data(data1, data2):
    if data1 is None:
        return
    for b1, b2 in zip(data1, data2):
        b1 = b1 if type(b1) != str else ord(b1)
        b2 = b2 if type(b2) != str else ord(b2)
        logging.error("%4d %4d" % (b1, b2))
    if len(data1) != len(data2):
        logging.error("Mismatched lengths: %d %d" % (len(data1), len(data2)))
    return None

class TestFlatePNG(unittest.TestCase):
    
    def test_flate_png(self):
        b64 = 'AAAAAAD//wACAAA2AAAAAQAADwAAAgEAACcAAQL/AAAzAP8AAgAANgACAAEAAO8AAAABAAF1AAAAAgAANgADAAEAAfsAAAACAAA2AAQCAAAAAAABAgAAAAAAAQIAAAAAAAECAAAAAAABAgAAAAAAAQIAAAAAAAECAAAAAAABAQECBXx8AAIAAAGHAAAAAgAANgAMAAEDCcMAAAACAAA2AA0CAAAAAAABAgAAAAAAAQIAAAAAAAECAAAAAAABAgAAAAAAAQIAAAAAAAECAAAAAAABAgAAAAAAAQABBxI2AAAEAfn5AAAWAgAAAAAAAQIAAAAAAAECAAAAAAABAgAAAAAAAQIAAAAAAAECAAAAAAABAgAAAAAAAQIAAAAAAAEAAQ6fJgAAAAIAADYAHwIAAAAAAAECAAAAAAABAgAAAAAAAQIAAAAAAAECAAAAAAABAgAAAAAAAQABESDsAAAAAgAANgAmAAAAAAD//wIAAAAAAAACARp0hgEBAgAA/eAAAA=='
        predictor, columns, colors, bpc = (12, 6, 1, 8)

        data = base64.b64decode(b64)
        d1, error1 = flate_png_orig(data, predictor, columns, colors, bpc)

        assert d1 is None
        assert error1 is not None

        data = base64.b64decode(b64)
        d2, error2 = flate_png(data, predictor, columns, colors, bpc)

        assert d2 is not None
        assert error2 is None

    def test_flate_png_filter_0(self):
        # None filter
        data, nc, nr, bpc, ncolors = create_data(nc=5, nr=7, bpc=8, ncolors=4)
        d1, error1 = flate_png_orig(data, 12, nc, ncolors, bpc) 

        data, nc, nr, bpc, ncolors = create_data(nc=5, nr=7, bpc=8, ncolors=4)
        d2, error2 = flate_png(data, 12, nc, ncolors, bpc)

        print_data(d1, d2)
        assert d1 == d2 

    def test_flate_png_filter_1(self):
        # Sub filter
        data, nc, nr, bpc, ncolors = create_data(nc=2, nr=3, bpc=8, ncolors=4, filter_type=1)
        d1, error1 = flate_png_orig(data, 12, nc, ncolors, bpc) 

        data, nc, nr, bpc, ncolors = create_data(nc=2, nr=3, bpc=8, ncolors=4, filter_type=1)
        d2, error2 = flate_png(data, 12, nc, ncolors, bpc)

        print_data(d1, d2)
        #assert d1 == d2

    def test_flate_png_filter_2(self):
        # Up filter
        data, nc, nr, bpc, ncolors = create_data(nc=5, nr=7, bpc=8, ncolors=4, filter_type=2)
        d1, error1 = flate_png_orig(data, 12, nc, ncolors, bpc) 

        data, nc, nr, bpc, ncolors = create_data(nc=5, nr=7, bpc=8, ncolors=4, filter_type=2)
        d2, error2 = flate_png(data, 12, nc, ncolors, bpc)

        print_data(d1, d2)
        assert d1 == d2 

    def test_flate_png_filter_3(self):
        # Avg filter
        data, nc, nr, bpc, ncolors = create_data(nc=5, nr=7, bpc=8, ncolors=4, filter_type=3)
        d2, error2 = flate_png(data, 12, nc, ncolors, bpc)

        assert d2
        assert error2 is None

    def test_flate_png_filter_4(self):
        # Paeth filter
        data, nc, nr, bpc, ncolors = create_data(nc=5, nr=7, bpc=8, ncolors=4, filter_type=4)
        d2, error2 = flate_png(data, 12, nc, ncolors, bpc)

        assert d2
        assert error2 is None

    def test_flate_png_alt_filter_1(self):
        width = 32
        bit_depth = 8
        channels = 1
        color_type = 0
        pixel_depth = 8
        rowbytes = 32
        filter = 1
        data = [ 0x00,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01, ]
        expected = [ 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1c,0x1d,0x1e,0x1f, ]

        dataf = prepend_data_with_filter(data, filter)
        result, error = flate_png_impl(dataf, 12, width, channels, bit_depth)

        assert error is None
        expected = array.array('B', expected)
        assert expected == result, "e: %r\nr: %r" % (expected, result)

    def test_flate_png_alt_filter_2(self):
        width = 32
        bit_depth = 8
        channels = 3
        color_type = 2
        pixel_depth = 24
        rowbytes = 96
        filter = 2
        prev_row = [ 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, ]
        data = [ 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00, ]
        expected = [ 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, ]

        prev_rowf = prepend_data_with_filter(prev_row, 0)
        dataf = prepend_data_with_filter(data, filter)
        prev_rowf.extend(dataf)
        dataf = prev_rowf
        result, error = flate_png_impl(dataf, 12, width, channels, bit_depth)

        assert error is None
        prev_rowa = array.array('B', prev_row)
        prev_rowa.extend(expected)
        expected = prev_rowa
        assert expected == result, "e: %r\nr: %r" % (expected, result)

    def test_flate_png_alt_filter_3(self):

        width = 32
        bit_depth = 8
        channels = 1
        color_type = 0
        pixel_depth = 8
        rowbytes = 32
        filter = 3
        prev_row = [ 0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0xe3,0xc9,0xf1,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f, ]
        data = [ 0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x69,0x02,0xe4,0xb5,0xc3,0xa1,0xff,0x31,0x51,0xcf,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00, ]
        expected = [ 0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0xe8,0xb5,0x7e,0x65,0x5a,0x46,0x61,0xa1,0xe1,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f,0x7f, ]

        prev_rowf = prepend_data_with_filter(prev_row, 0)
        dataf = prepend_data_with_filter(data, filter)
        prev_rowf.extend(dataf)
        dataf = prev_rowf
        result, error = flate_png_impl(dataf, 12, width, channels, bit_depth)

        assert error is None
        prev_rowa = array.array('B', prev_row)
        prev_rowa.extend(expected)
        expected = prev_rowa
        assert expected == result, "e: %r\nr: %r" % (expected, result)

    def test_flate_png_alt_filter_4(self):
        width = 32
        bit_depth = 8
        channels = 1
        color_type = 0
        pixel_depth = 8
        rowbytes = 32
        filter = 4
        prev_row = [ 0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a,0x2b,0x2c,0x2d,0x2e,0x2f,0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3a,0x3b,0x3c,0x3d,0x3e,0x3f, ]
        data = [ 0x20,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01, ]
        expected = [ 0x40,0x41,0x42,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4a,0x4b,0x4c,0x4d,0x4e,0x4f,0x50,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x59,0x5a,0x5b,0x5c,0x5d,0x5e,0x5f, ]

        prev_rowf = prepend_data_with_filter(prev_row, 0)
        dataf = prepend_data_with_filter(data, filter)
        prev_rowf.extend(dataf)
        dataf = prev_rowf
        result, error = flate_png_impl(dataf, 12, width, channels, bit_depth)

        assert error is None
        prev_rowa = array.array('B', prev_row)
        prev_rowa.extend(expected)
        expected = prev_rowa
        assert expected == result, "e: %r\nr: %r" % (expected, result)

    def util_test_flate_png_alt_from_png_log_file(self, filename):

        with open(filepath(filename)) as f:
            data = array.array('B')
            expected = array.array('B')
            width = 0
            bit_depth = 0
            channels = 0
            color_type = 0
            pixel_depth = 0
            rowbytes = 0
            filter = 0
            nrows = 0

            for l in f.readlines():

                if l.startswith("PASS:"):
                    break

                l = l.split(' = ')
                var = l[0]
                val = l[1]

                if var == 'width':
                    width = int(val)

                elif var == 'bit_depth':
                    bit_depth = int(val)

                elif var == 'channels':
                    channels = int(val)

                elif var == 'color_type':
                   color_type = int(val)

                elif var == 'pixel_depth':
                    pixel_depth = int(val)

                elif var == 'rowbytes':
                    rowbytes = int(val)

                elif var == 'filter':
                    filter = int(val)

                elif var == 'data':
                    d = ast.literal_eval(val)
                    data.append(filter)
                    data.extend(d)

                elif var == 'expected':
                    e = ast.literal_eval(val)
                    expected.extend(e)
                    nrows += 1

            bytes_per_pixel = pixel_depth // 8

            logging.error("width: %d" % width)
            logging.error("bit_depth: %d" % bit_depth)
            logging.error("channels: %d" % channels)
            logging.error("color_type: %d" % color_type)
            logging.error("pixel_depth: %d" % pixel_depth)
            logging.error("rowbytes: %d" % rowbytes)
            logging.error("filter: %d" % filter)
            logging.error("bytes_per_pixel: %d" % bytes_per_pixel)
            logging.error("expected: %r" % len(expected))
            logging.error("data: %r" % len(data))

            assert color_type in [
                        0, # Grayscale (Y)
                        2, # Truecolor (RGB)
                        # 3 Indexed is not supported (Palette)
                        4, # Grayscale with alpha (YA)
                        6, # Truecolor with alpha (RGBA)
                    ]
            assert filter in [0, 1, 2, 3, 4]
            assert channels * bit_depth == pixel_depth
            assert (pixel_depth // 8) * width == rowbytes
            assert 0 == pixel_depth % 8 # can't support pixels with bit_depth < 8
            assert 8 == bit_depth # ideally, we should test bit_depth 16 also
            assert nrows * (1 + width * bytes_per_pixel) == len(data) # 1 filter byte preceeding each row
            assert nrows * width * bytes_per_pixel == len(expected)

        result, error = flate_png_impl(data, 12, width, channels, bit_depth)

        import pickle
        with open(filepath('./result.pickle'), 'wb') as f:
            pickle.dump(result, f)
        with open(filepath('./expected.pickle'), 'wb') as f:
            pickle.dump(expected, f)

        assert error is None
        assert expected == result


    def test_flate_png_alt_file_f01n2c08(self):
        self.util_test_flate_png_alt_from_png_log_file("./f01n2c08.png.log")

    def test_flate_png_alt_file_f02n2c08(self):
        self.util_test_flate_png_alt_from_png_log_file("./f02n2c08.png.log")

    def test_flate_png_alt_file_f03n2c08(self):
        self.util_test_flate_png_alt_from_png_log_file("./f03n2c08.png.log")

    def test_flate_png_alt_file_f04n2c08(self):
        self.util_test_flate_png_alt_from_png_log_file("./f04n2c08.png.log")

    def test_flate_png_alt_file_basn2c08(self):
        self.util_test_flate_png_alt_from_png_log_file("./basn2c08.png.log")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
