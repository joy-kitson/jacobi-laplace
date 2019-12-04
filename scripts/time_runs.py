#!/usr/bin/env python2

import os
import re
import subprocess
import numpy as np
import pandas as pd
import argparse

TIME_REGEX = r'total:\s([0-9]+.[0-9]+)\ss'

def parse_args():
    parser = argparse.ArgumentParser()
  
    #positional args
    parser.add_argument('app_paths', nargs='+',\
                        help='Tells the script where to find the executables to time')
    #optional args
    parser.add_argument('--row_range', type=int, nargs=2, default=[10,13],\
                        help='The range of rows to run with, as powers of 2' +\
                             '(ex: \"--row_range 1 3\" will time with 2, 4, and 8 rows)')
    parser.add_argument('--col_range', type=int, nargs=2, default=[10,13],\
                        help='The range of columns to run with, as orders of magnitiude' +\
                             '(ex: \"--col_range 1 3\" will time with 2, 4, and 8 columns)')
    parser.add_argument('--iters', type=int, default=10,\
                        help='The number of times to run each configuration before averaging the runtimes')
    parser.add_argument('--out_path', default='{}_times.csv',\
                        help='Tells the script where to write its output to')
    
    parser.add_argument('--env_vars', nargs='+', default=[],\
                        help='Specifies the values of enivronment variables to run with. Entries' +\
                             ' should be of the form "VAR=value"')

    return parser.parse_args()


def set_env_vars(env_vars):
    for arg in env_vars:
        var, value = arg.split('=')

        if os.environ.get(var) is None:
            print('Creating new environment variable, {}'.format(var))
        else:
            print('Value of {} originally set to {}'.format(var, os.environ[var]))
        os.environ[var] = value
        print('Value of {} changed to {}'.format(var, os.environ[var]))


def time_run(app, rows, cols):
    # time using the in-built bash command
    cmd = '{} {} {}'.format(os.path.join('.', app), rows, cols)
    output = subprocess.check_output(cmd, \
                                     stderr=subprocess.STDOUT, \
                                     shell=True
                                    )
    output = str(output)
    match = re.search(TIME_REGEX, output)
    time = float(match.group(1))
    
    return time


def main():
    args = parse_args()
    row_min, row_max = args.row_range
    col_min, col_max = args.col_range
    out_path = args.out_path
    iters = args.iters
    apps = args.app_paths
    set_env_vars(args.env_vars)

    def collect_timing_data(app, out_file):
        data = [[2**c for c in range(col_min, col_max + 1)]]
        app_name = os.path.basename(app)
        out_file.write('Input Size,{}\n'.format(app_name))

        data_row = []
        for c in range(col_min, col_max + 1):
            col_arg = 2**c
            row_arg = col_arg
            
            total_time = 0
            for i in range(iters):
                total_time += time_run(app, row_arg, col_arg)
            ave_time = float(total_time) / iters
            data_row.append(ave_time)
            
            print('{} averaged {}s with {} rows and {} cols'\
                  .format(app_name, ave_time, row_arg, col_arg))
            out_file.write('{} x {},{}\n'.format(row_arg, col_arg, ave_time))

        data.append(data_row)
        return data

    for app in apps:
        with open(out_path.format(app), 'w+') as out_file:
            data = collect_timing_data(app, out_file)


if __name__ == '__main__':
    main()
