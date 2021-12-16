from __future__ import print_function

import os
import sys
import io
import argparse
import time
import collections

__version__ = '0.4.0'

enable_verbose = False

class LogDevice:
    def __init__(self):
        self.filelog = collections.defaultdict(list)

    def add_filelog(self, filename, msg):
        self.filelog[filename].append(msg)

    def print_filelog(self):
        for filename, msgs in self.filelog.items():
            print(filename)
            for msg in msgs:
                print(msg)
            print()

    def add_log(self, msg):
        print(msg)

    def __str__(self):
        self.print_filelog()


class CodingPatch:
    def __init__(self, log_dev, fullpath, lines):
        self.log_dev = log_dev
        self.fullpath = fullpath
        self.lines = lines
        self.file_changed = False
        self.found_non_ascii = False

    def get_lines(self):
        return self.lines

    def is_file_changed(self):
        return self.file_changed

    def update_copyright(self, copyright_year):
        for index, line in enumerate(self.lines):
            # The format should be:
            # 1.   Copyright 20xx Intel Corporation.
            # 2.   Copyright 20xx - 20yy Intel Corporation.
            if 'Copyright' in line and 'Intel Corporation' in line:
                # If copyright date is not present
                if str(copyright_year) not in line:
                    new_line = ''
                    self.log_dev.add_filelog(self.fullpath, 'Find copyright mismatch at line #{}'.format(index + 1))
                    self.log_dev.add_filelog(self.fullpath, line.rstrip('\n'))
                    index1 = line.find('Intel Corporation')
                    index2 = line.find('-')
                    if index2 == -1:
                        new_line = line[:index1] + '- ' + str(copyright_year) + \
                                  ' ' + line[index1:]
                    else:
                        new_line = line[:index2] + '- ' + str(copyright_year) + \
                                  ' ' + line[index1:]
                    self.log_dev.add_filelog(self.fullpath, 'Update copyright date -->')
                    self.log_dev.add_filelog(self.fullpath, new_line.rstrip('\n'))
                    self.lines[index] = new_line
                    self.file_changed = True

    def trim_tabs(self):
        for index, line in enumerate(self.lines):
            # Replace tab with spaces
            if '\t' in line:
                self.file_changed = True
                self.log_dev.add_filelog(self.fullpath, 'Correct tabs at line #{}'.format(index + 1))
                new_line = line.replace('\t', '  ')
                self.lines[index] = new_line

    def trim_tailspaces(self):
        file_changed = False
        for index, line in enumerate(self.lines):
            # Trim tailing whitespaces
            new_line = line.rstrip()
            if '\n' in line:
                new_line = new_line + '\n'
            if len(line) != len(new_line):
                file_changed = True
                self.log_dev.add_filelog(self.fullpath, 'Correct tailing whitespaces at line #{}'.format(index + 1))
                self.lines[index] = new_line

    def is_found_non_ascii(self):
        return self.found_non_ascii

    def check_ascii(self):
        for index, line in enumerate(self.lines):
            for column, c in enumerate(line):
                if ord(c) > 0x7F:
                    self.found_non_ascii = True
                    self.log_dev.add_filelog(self.fullpath, 'Found non-ascii code in line #{} [{}]'.format(index, column))


def set_parser():
    parser = argparse.ArgumentParser('Process pending files before commit')
    parser.add_argument('root', help='The repo root directory')
    parser.add_argument('filelist', nargs='+', help='All pending files')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('--verbose', action='store_true', help='Show more information')
    parser.add_argument('--copyright', type=int, help='Update the copyright year for pending files, if "0", then current time is used')
    parser.add_argument('--notabs', action='store_true', help='Replace tab with spaces')
    parser.add_argument('--notailspaces', action='store_true', help='Trim tailing whitespaces')
    parser.add_argument('--checkascii', action='store_true', help='Check only ASCII char.')
    return parser.parse_args()


def get_pending_files(rootdir, filelist):
    pending_files = [rootdir + '/' + f for f in filelist]
    return pending_files


def open_text_file(fullpath, filename_ext):
    encode_list = []
    encode_mode = ''
    lines = []
    open_file_success = True

    if filename_ext in ['.uni']:
        encode_list = ['utf-16', 'utf-8', None]
    else:
        encode_list = [None, 'utf-16', 'utf-8']

    for encode_mode in encode_list:
        try:
            with io.open(fullpath, 'r', encoding=encode_mode) as f:
                lines = f.readlines()
        except:
            # Continue next encoding type
            continue;
        break;
    else:
        print('No supported encoding. Skip file {}'.format(fullpath))
        open_file_success = False

    return open_file_success, encode_mode, lines


def write_text_file(fullpath, encode_mode, lines):
    with io.open(fullpath, 'w', encoding=encode_mode) as f:
        for line in lines:
            f.write(line)


def print_change_info(log_dev, rootdir, filelist):
    log_dev.add_log('Change information:')
    log_dev.add_log('RootDir: {}'.format(rootdir))
    for f in filelist:
        log_dev.add_log('File   : {}'.format(f))
    log_dev.add_log('')


def print_full_path(log_dev, pending_files):
    log_dev.add_log('File full path:')
    for f in pending_files:
        log_dev.add_log(f)
    log_dev.add_log('')


def main():
    """This is the tool to apply patches before code review and submit.

    This supports follow functions:
    1. Patch copyright date.
    2. Replace TAB with spaces.
    3. Trim the tailing spaces.
    4. Check non-ASCII code.
    """
    # Set up arg parser
    args = set_parser()
    enable_verbose = args.verbose
    rootdir = args.root
    filelist = args.filelist

    log_dev = LogDevice()

    # Show input #
    if enable_verbose:
        print_change_info(log_dev, rootdir, filelist)


    # Get full path for feils
    pending_files = get_pending_files(rootdir, filelist)
    if enable_verbose:
        print_full_path(log_dev, pending_files)

    any_file_changed = False
    abort_commit = False

    for fullpath in pending_files:
        filename_base, filename_ext = os.path.splitext(fullpath)
        #
        # Skip deleted file or if file does not exist
        if not os.path.isfile(fullpath):
            continue

        # Skip binary file
        if filename_ext in ['.bin', '.rom', '.pdb', '.fd', '.obj', \
                            '.pdf', '.doc', '.exe', '.efi']:
            if enable_verbose:
                log_dev.add_log('Skip binary file: {}'.format(fullpath))
            continue

        # Support unicode file and ascii file
        open_file_success, encode_mode, lines = open_text_file(fullpath, filename_ext)
        if not open_file_success:
            continue

        #
        # Apply patches here
        #
        coding_patch = CodingPatch(log_dev, fullpath, lines)

        # Update copyright date
        if args.copyright != None:
            copyright = args.copyright
            if copyright == 0:
                copyright = int(time.strftime('%Y'))
            coding_patch.update_copyright(copyright)

        # Trim tabs
        if args.notabs:
            coding_patch.trim_tabs()

        # Trim tailing whitespaces
        if args.notailspaces:
            coding_patch.trim_tailspaces()

        # Check ASCII char
        # This doesn't change file content but show error message.
        if args.checkascii:
            if filename_ext not in ['.uni']:
                coding_patch.check_ascii()

        #
        # End of patches
        #

        # If content is changed, write the file
        if coding_patch.is_file_changed():
            any_file_changed = True
            write_text_file(fullpath, encode_mode, coding_patch.get_lines())

        if coding_patch.is_found_non_ascii():
            abort_commit = True;

    #
    # Dump the code patch messages
    #
    log_dev.print_filelog()

    if any_file_changed or abort_commit:
        # stop the commit.
        sys.exit(1)

if __name__ == '__main__':
    main()
