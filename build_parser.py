#!/usr/bin/python

import sys
import getopt
import re
import os

def realpath2relpath(realpath, start): 
    if start and realpath.startswith(start): 
        return os.path.relpath(realpath, start) 
    else: 
        return realpath

def main(argv):
    project = 'make'
    root_path = ''
    build_tool = r'^\s*[\w_-]*(gcc|g\+\+)\s'
    current_path = ''
    join_line1 = False
    join_line2 = False
    defines = set()
    includes = set()

    opts, ip = getopt.getopt(argv, "hn:r:t:", ["project=", "root_path=", "build_tool="])
    for opt, arg in opts:
        if opt == "-h":
            print(
                'Usage: build_parser [-h -n -r -t] build_output_file\n'
                '-h Print this help\n'
                '-n, --project=project_name\n'
                '\tSet project name\n'
                '-r, --root_path=root_path\n'
                '\tSet the root path of the source code\n'
                '-t, --build_tool=build_tool_name\n'
                '\tSet the build tool name, multiple build tools can be set.\n'
                '\tFor example, --build_tool="gcc|sh4gcc|sh4-linux-gcc"\n'
                '\tBy default, all the tools end of gcc can be recognized\n'
                )
                
            sys.exit(0)
        elif opt in ['-n', '--project']:
            project = arg
        elif opt in ['-r', '--root_path']:
            root_path = arg
        elif opt in ['-t', '--build_tool']:
            build_tool = arg
        else:
            sys.exit(2)

    build_file = open(ip[0], 'r')
    files_file = open(project + '.files', 'w')

    match_tool = re.compile(build_tool)
    match_path = re.compile(r'^make\s*-C\s*(\S+)\s')
    match_file = re.compile(r'(\S+\.(c|cpp|cc))\s')
    match_define = re.compile(r'-D\s*(\S+)\s')
    match_include = re.compile(r'(-I|-idirafter|-isystem|-iquote|-isysroot|--sysroot)\s*(\S+)\s')
    for line in build_file:
        if line.rstrip().endswith('\\'):
            join_line2 = True
        else:
            join_line2 = False

        match = match_path.search(line)
        if match:
            current_path=match.group(1)
            continue

        if not match_tool.search(line):
            if not join_line1:
                continue

        join_line1 = join_line2

        match = match_file.search(line)
        if match:
            s = match.group(1)
            path = os.path.join(current_path, s)
            if path.startswith('/'):
                path = realpath2relpath(path, root_path)
            files_file.write(path + '\n')

        matchs = match_define.finditer(line)
        for match in matchs:
            s = match.group(1)
            if not s:
                continue
            df = s.replace('=', ' ').replace('"', '')
            defines.add("#define " + df)

        matchs = match_include.finditer(line)
        for match in matchs:
            s = match.group(2)
            if not s:
                continue
            path = os.path.join(current_path, s)
            if path.startswith('/'):
                path = realpath2relpath(path, root_path)
            includes.add(path)

    build_file.close()
    files_file.close()

    config_file = open(project + '.config', 'w')
    include_file = open(project + '.includes', 'w')

    for item in defines:
        config_file.write('%s\n' % item)
    for item in includes:
        include_file.write('%s\n' % item)

    config_file.close()
    include_file.close()

if __name__ == "__main__":
    main(sys.argv[1:])
