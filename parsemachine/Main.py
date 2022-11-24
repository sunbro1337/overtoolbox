#!/usr/bin/env python3.8
"""
---Pyinstaller rules---
pyinstaller Main.py -n "parsemachine" --onefile
"""
#import re
import argparse
import sys
import difflib


def find_line(filePath, string, count=None):
    file = open(filePath, "r")
    loop_count = 0
    for line in file:
        if count and count < loop_count:
            break
        if string in line:
            print(line.replace("\n", ""))
            loop_count += 1
    file.close()


def rm_lines(filePath, string):
    file = open(filePath, "r")
    result_file = open(f"{filePath}_trim", 'w')
    for line in file:
        if string not in line:
            result_file.write(line)
    file.close()
    result_file.close()


def collect_lines(file_path, string, sim_percent):

    def similar(seq1, seq2, percent):
        return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > percent

    def check_lines(list, line, sim_percent):
        if len(list) == 0:
            list.append(line)
            return list
        for i in list:
            print(i, line)
            if similar(i, line, sim_percent):
                return list
        list.append(line)
        return list

    file = open(file_path, 'r')
    result_strings = []
    for line in file:
        if string in line:
            check_lines(result_strings, line, sim_percent)
    file.close()
    result_file = open(f"{file_path}_filtered", 'w')
    for i in result_strings:
        result_file.write(i)
    result_file.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog="ParseMachine")
    arg_parser.add_argument("-f", "--file", help="Path to a file that need parse")
    arg_parser.add_argument("-s", "--string", help="Substring to parse")
    arg_parser.add_argument("-c", "--count", help="Count of loop find line", default=1)
    arg_parser.add_argument("--collect", help="Collect filtered file", action="store_true")
    arg_parser.add_argument("--rmstr", help="Remove founded string", action="store_true")
    arg_parser.add_argument('--spercent', help='Percent of similarity for --rmstr', default=0.9, type=float)
    args = arg_parser.parse_args()

    if args.file == None and args.string == None:
        print("Argument is not recognized, enter [-h] for help.")
        sys.exit(1)

    if args.rmstr:
        find_line(args.file, args.string, int(args.count))
        rm_lines(args.file, args.string)
    elif args.collect:
        collect_lines(args.file, args.string, args.spercent)
    else:
        print("Argument is not recognized, enter [-h] for help.")