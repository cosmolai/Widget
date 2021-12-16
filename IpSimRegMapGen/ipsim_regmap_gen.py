#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Tool to generate register map from header files.
# Date: Feb 18, 2021
# Author: Lai, Cosmo <cosmo.lai@intel.com>

"""
IPSIM register map generator.
This requires PyCLibrary installed.
"""
from __future__ import (print_function)
import os
import os.path
import sys
import argparse
import re
from os import path
from pyclibrary import CParser


regmap = []

parser_cachefile = r"ipsim_regmap.cache"

copyright_text = """
/** @file
  {}

  NOTE: THIS FILE IS AUTO GENERATED. DO NOT MODIFY THIS FILE.

  @copyright
  INTEL CONFIDENTIAL
  Copyright 2021 Intel Corporation. <BR>

  The source code contained or described herein and all documents related to the
  source code ("Material") are owned by Intel Corporation or its suppliers or
  licensors. Title to the Material remains with Intel Corporation or its suppliers
  and licensors. The Material may contain trade secrets and proprietary    and
  confidential information of Intel Corporation and its suppliers and licensors,
  and is protected by worldwide copyright and trade secret laws and treaty
  provisions. No part of the Material may be used, copied, reproduced, modified,
  published, uploaded, posted, transmitted, distributed, or disclosed in any way
  without Intel's prior express written permission.

  No license under any patent, copyright, trade secret or other intellectual
  property right is granted to or conferred upon you by disclosure or delivery
  of the Materials, either expressly, by implication, inducement, estoppel or
  otherwise. Any license under such intellectual property rights must be
  express and approved by Intel in writing.

  Unless otherwise agreed by Intel in writing, you may not remove or alter
  this notice or any other notice embedded in Materials by Intel or
  Intel's suppliers or licensors in any way.
**/

"""

regmapentry_start_template = "IPSIM_REGMAP_ENTRY m{endpoint}_RegMap[] = {{\n"

"""
Refer to the struct definition in IpSim.h

typedef struct {
  UINT32                       Offset;
  UINT32                       Width;
  UINT64                       Value;
  char*                        Name;
  UINT64                       ReservedBitMap;
  IPSIM_REGMAP_ENTRY_AUXILIARY Auxiliary;
} IPSIM_REGMAP_ENTRY;
"""
regmapentry_template = "  {{0x{offset:08X}, {width:4d}, 0x{default:08X}, \"{regname:48}\", 0x{rsvdbits}, {{0}} }}"

regmapentry_end_template = """
}};

IPSIM_REGMAP_TABLE m{endpoint}_RegMapTable = {{
  {{
    {endpoint}, //EndPoint
    sizeof (m{endpoint}_RegMap) / sizeof (IPSIM_REGMAP_ENTRY), //Size
    0, //Socket
    0, //Index
    \"{endpoint}\" //Name
  }},
  m{endpoint}_RegMap
}};

"""

regmaptablelist_template = """
IPSIM_REGMAP_TABLE *mRegMapTableList[] = {{
{}
}};

UINT32 mRegMapTableListSize = sizeof (mRegMapTableList) / sizeof (IPSIM_REGMAP_TABLE *);
"""

regmapdef_template = """
typedef enum {{
{}
  EnumRegMapEndPointMax
}} REGMAP_ENDPOINT;

extern IPSIM_REGMAP_TABLE *mRegMapTableList[];
extern UINT32 mRegMapTableListSize;

"""


def gen_regmap(headerfiles, cache_file_path):
    print("Parser headers. This will take long time. Be patient...")
    parser = CParser(headerfiles, cache=cache_file_path)
    macros = parser.defs['macros']

    # fine all *_REG
    # get regname and offset
    for key, val in macros.items():
        if val != '' and key.endswith("_REG"):
            entry = {}
            entry["regname"] = key[0:key.rfind("_REG")]
            entry["offset"] = int(val.strip("(U)"), base=16)
            entry["default_value"] = 0
            regmap.append(entry)

    # calculate the reserved bits and store as string type at "rsvdbits" column in entry
    for entry in regmap:
        reg_name = entry["regname"]
        # union_name_alias and struct_name_alias are aliases of the name of each "union" and the name of "struct" in that
        # "union" respectively in input C files in which we are going to use to extract the fields of the register
        union_name_alias = parser.defs["types"][reg_name + "_STRUCT"].type_spec.split()[1]
        struct_name_alias = parser.defs["unions"][union_name_alias]["members"][0][1].type_spec.split()[1]
        bit_fields = []
        # extract the name of each bit field and corresponding length in the register
        for struct_entry in parser.defs["structs"][struct_name_alias]["members"]:
            name_length_pair = []
            name_length_pair.append(struct_entry[0])
            name_length_pair.append(struct_entry[3])
            bit_fields.append(name_length_pair)

        # initilize with 1 which prevents rsvdbits from invalid shifts
        rsvdbits = 1
        # total bits of the register
        total_bits = 0
        bit_fields.reverse()
        for field in bit_fields:
            # accumulate total bits
            total_bits += field[1]
            # if the field is either rsvd_# or rsvd_#_#, set all of the bits of corresponding positions to 1
            # we accept both of two types because some of files uses the former one and some uses the latter one
            match = re.match(r"^rsvd(_([0-9]+)){1,2}$", field[0])
            for _ in range(field[1]):
                rsvdbits <<= 1
                if match:
                    rsvdbits |= 1
        # eliminate the first bit which is dummy
        rsvdbits &= ~(1 << total_bits)
        entry["rsvdbits"] = format(rsvdbits, '0' + str(total_bits // 4) + 'X')

    # get width and endpoint
    for entry in regmap:
        entry["width"] = int(macros.get(entry['regname']+"_WIDTH", 0))
        entry["endpoint"] = macros.get(entry['regname']+"_ENDPOINT", 0)
        if entry["width"] == 0 or entry["endpoint"] == 0:
            print("ERROR: Cannot find associated width/endpoint info of register {}\n".format(entry['regname']))


def get_default_value(headerfiles):
    """ assume the pattern is:
        /** REGISTER_NAME_MACRO desc:
        * Register default value:        0x02110001
        * ...
        * ...
        */
    """
    # go through all headef files
    for headerfile in headerfiles:
        with open(headerfile, "r") as file:
            lines = file.readlines()
            # check default value pattern
            for index, line in enumerate(lines):
                if line.find("Register default value:") > 0:
                    # get last element of split string
                    split_str = line.split(sep=":")
                    default_value = int(split_str[-1].strip(), base=16)
                    # fine the key of regmap
                    previous_line = lines[index-1]
                    split_str = previous_line.split()
                    regname = split_str[-2].strip()
                    # update regmap
                    for entry in regmap:
                        if entry["regname"] == regname:
                            entry["default_value"] = default_value


def sort_by_endpoint(elem):
    return elem["endpoint"]


def sort_by_offset(elem):
    return elem["offset"]


def output_regmap(output_folder):
    regmap.sort(key=sort_by_offset)
    regmap.sort(key=sort_by_endpoint)

    endpoint_list = []

    start_regmap_array = False
    with open(output_folder+"/IpSimRegMap.c", "w") as file:
        file.write(copyright_text.format("Create register map table"))
        file.write("#include <IpSim.h>\n")
        file.write("#include <IpSimRegMap.h>\n\n")

        for entry in regmap:
            if entry["endpoint"] not in endpoint_list:
                if start_regmap_array:
                    file.write(regmapentry_end_template.format(endpoint=endpoint_list[-1]))
                endpoint_list.append(entry["endpoint"])
                start_regmap_array = True
                file.write(regmapentry_start_template.format(endpoint=entry["endpoint"]))
            else:
                file.write(",\n")
            file.write(regmapentry_template.format(offset=entry["offset"], width=entry["width"], default=entry["default_value"], regname=entry["regname"], rsvdbits=entry["rsvdbits"]))
        if start_regmap_array:
            file.write(regmapentry_end_template.format(endpoint=endpoint_list[-1]))
        tempstr = ""
        for endpoint in endpoint_list:
            if len(tempstr) != 0:
                tempstr += ",\n"
            tempstr += "  &m" + endpoint + "_RegMapTable"
        file.write(regmaptablelist_template.format(tempstr))
        print("Generate file: " + output_folder + "/IpSimRegMap.c")

    with open(output_folder+"/IpSimRegMap.h", "w") as file:
        file.write(copyright_text.format("IpSim register map definitions"))
        file.write("#ifndef __IPSIM_REGMAP_H__\n")
        file.write("#define __IPSIM_REGMAP_H__\n\n")
        tempstr = ""
        for endpoint in endpoint_list:
            if len(tempstr) != 0:
                tempstr += "\n"
            tempstr += "  {},".format(endpoint)
        file.write(regmapdef_template.format(tempstr))
        file.write("#endif\n")
        print("Generate file: " + output_folder + "/IpSimRegMap.h")


def main():
    argparser = argparse.ArgumentParser("Get input header files and output folder.")
    argparser.add_argument("-i", "--include_file", action="append", help="Include register header file.")
    argparser.add_argument("-o", "--output_folder", help='Output folder.')
    arg = argparser.parse_args()

    headerfiles = arg.include_file
    if headerfiles == None:
        print("ERROR: No input register header file.")
        print("")
        argparser.print_help()
        exit(0)
    else:
        print("Register headers:")
        for h in headerfiles:
            print("  " + h)

    output_folder = arg.output_folder
    if output_folder == None:
        print("ERROR: No output folder.")
        print("")
        argparser.print_help()
        exit(0)
    else:
        print("Output folder is:")
        print("  " + output_folder)

    for h in headerfiles:
        if not path.isfile(h):
            print("ERROR: {} is not a file.".format(h))
            exit(0)

    if not path.isdir(output_folder):
        print("ERROR: {} is not a folder.".format(output_folder))
        exit(0)

    gen_regmap(headerfiles, output_folder + "/" + parser_cachefile)
    get_default_value(headerfiles)

    #print("Dump RegMap:")
    #for temp in regmap:
    #    print(temp)

    output_regmap(output_folder)


if __name__ == '__main__':
    main()
