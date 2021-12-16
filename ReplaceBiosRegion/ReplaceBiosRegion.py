#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Lai Cosmo'
__copyright__ = "Copyright 2019"
#__credits__ = ["Lai Cosmo"]
#__license__ = "None"
__version__ = "0.1.0"
__maintainer__ = "Lai Cosmo"
__email__ = "cosmo.lai@intel.com"
__status__ = "First Release"

import os
import argparse
import array

enable_verbose = False

def verbose_print(msg):
    if enable_verbose:
        print(msg)

def error_print(msg):
    print(msg)

def output_print(msg):
    print(msg)

def set_parser():
    parser = argparse.ArgumentParser('Replace BIOS region of IFWI binary')
    parser.add_argument('ifwi_binary', help='IFWI binary')
    parser.add_argument('bios_rom', help='BIOS rom')
    parser.add_argument('-o', '--output', dest='output_binary', default='outimage.bin', help='Output binary name. Default is outimage.bin')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show more information')
    return parser.parse_args()

def main():
    """This tool replaces the BIOS region in IFWI binary.
    """

    # Set up arg parser
    args = set_parser()
    ifwi_bin = args.ifwi_binary
    bios_rom = args.bios_rom
    output_bin = args.output_binary
    global enable_verbose
    enable_verbose = args.verbose

    verbose_print('IFWI binary is : {}'.format(ifwi_bin))
    verbose_print('BIOS rom is    : {}'.format(bios_rom))
    verbose_print('Verbase is     : {}'.format(enable_verbose))

    error_input = False
    if not os.path.exists(ifwi_bin):
        error_print('Error: IFWI binary does not exist.')
        error_input = True
    if not os.path.exists(bios_rom):
        error_print('Error: BIOS rom does not exist.')
        error_input = True
    if error_input:
        return

    # ifwi_file = open(ifwi_bin, 'b')
    # bios_file = open(bios_rom, 'b')
    # out_file = open(output_bin, 'wb')
    # out_file.close()
    # bios_file.close()
    # ifwi_file.close()

    with open(ifwi_bin, 'rb') as ifwi_file, open(bios_rom, 'rb') as bios_file, open(output_bin, 'wb') as out_file:
        ifwi_byte_array = array.array('B', ifwi_file.read())
        ifwi_file_size = len(ifwi_byte_array)
        bios_byte_array = array.array('B', bios_file.read())
        bios_file_size = len(bios_byte_array)
        output_print('IFWI size        : 0x{:X}'.format(ifwi_file_size))
        output_print('BIOS size        : 0x{:X}'.format(bios_file_size))
        bios_region_base = (ifwi_byte_array[0x44] | ifwi_byte_array[0x45] << 8) << 12
        bios_region_end  = ((ifwi_byte_array[0x46] | ifwi_byte_array[0x47] << 8) + 1) << 12
        output_print('BIOS region base : 0x{:X}'.format(bios_region_base))
        output_print('BIOS region end  : 0x{:X}'.format(bios_region_end))
        if ifwi_file_size < bios_file_size:
            error_input('Error: IFWI size is smaller than BIOS size.')
            return
        out_file.write(ifwi_byte_array[:ifwi_file_size-bios_file_size])
        out_file.write(bios_byte_array)
        output_print('Output file: {}'.format(output_bin))

if __name__ == '__main__':
    main()
