#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Tool to validate yaml file.
# Date: 2022/02/22
#
# Version 0.1: Initial version.


import yaml
import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--input_file', help='Input yaml file')
    args = parser.parse_args()

    if args.input_file == None:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input_file):
        print('YAML file does not exist.')
        sys.exit(1)

    with open(args.input_file, 'r') as f:
        yaml_content = f.read()

    try:
        dictionaries = yaml.load_all(yaml_content, Loader=yaml.Loader)
        index = 0
        for dictionary in dictionaries:
            print('YAML document {}'.format(index))
            index = index + 1
            print(dictionary)
            print()
            print()
    except yaml.YAMLError as e:
        print('YAML formattting error!!!')
        print(str(e))
        sys.exit (1)

    print('YAML formatting correct.')


if __name__ == "__main__":
    main()
