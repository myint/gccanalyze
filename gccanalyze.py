#!/usr/bin/env python
#
# Copyright (C) 2012 Steven Myint
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""Do static analysis with GCC."""

__version__ = '0.1.2'

import argparse
import os
import subprocess
import sys


def directory(filename):
    """Return directory of filename."""
    directory_path = os.path.dirname(filename)
    return directory_path if directory_path else '.'


def split_warnings(warnings):
    """Split full warning text into individual warnings."""
    current = []
    for line in warnings.split('\n'):
        line = line.strip()
        if not line:
            continue

        current.append(line)
        if line.endswith(']') and '[-W' in line:
            yield '\n'.join(current)
            current = []

    if current:
        yield '\n'.join(current)


def filter_shadow(warnings):
    """Return filtered shadow warnings.

    Leave local shadow warnings.

    """
    filtered_lines = [
        line for line in split_warnings(warnings)
        if line and
        not line.endswith(" shadows a member of 'this' [-Wshadow]")]

    if len(filtered_lines) < 2:
        return ''
    else:
        return '\n'.join(filtered_lines)


def main(argv, standard_out):
    """Main function."""
    parser = argparse.ArgumentParser(description=__doc__, prog='gccanalyze')
    parser.add_argument('--include-directory', action='append', default=[],
                        help='search for headers here')
    parser.add_argument('--strict-shadow', action='store_true',
                        help='warn about all shadowing')
    parser.add_argument('--verbose', action='store_true',
                        help='echo GCC command')
    parser.add_argument('files', nargs='+',
                        help='files to analyze')

    args = parser.parse_args(argv[1:])

    base_command = [
        'gcc',
        '-O3',
        '-Wall',
        '-Wcast-qual',
        '-Wconversion',
        '-Wextra',
        '-Winit-self',
        '-Wlogical-op',
        '-Wmissing-include-dirs',
        '-Wnon-virtual-dtor',
        '-Wold-style-cast',
        '-Wpointer-arith',
        '-Wswitch-default',
        '-Wshadow',
        '-ansi',
        '-pedantic',
        '-fsyntax-only']

    options = ['-I' + include for include in args.include_directory]

    for filename in args.files:
        gcc_command = (
            base_command +
            options +
            ['-I' + directory(filename)] +
            ['-c', filename])

        if args.verbose:
            standard_out.write(' '.join(gcc_command) + '\n')
        process = subprocess.Popen(gcc_command,
                                   stderr=subprocess.PIPE)
        warnings = process.communicate()[1].decode('utf-8')

        if process.returncode != 0:
            standard_out.write(warnings + '\n')
        else:
            standard_out.write(
                (warnings if args.strict_shadow else filter_shadow(warnings)) +
                '\n')


if __name__ == '__main__':
    sys.exit(main())
