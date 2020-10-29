#!/usr/bin/env python

from __future__ import division

import sys
import os.path
import argparse
import itertools


def get_args():
    parser = argparse.ArgumentParser(description='Generates a bed or wig file from two bed files with the ratio of coverage', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--file1', required=True, help='the first bed file (the ratio is first/second)')
    parser.add_argument('--file2', required=True, help='the second bed file (the ratio is first/second)')
    parser.add_argument('--noNormalise', action='store_false', help="do not normalise files for read depth")
    parser.add_argument('--out', required=False, help='output file name, defaults to STDOUT')
    parser.add_argument('--format', default='bed', required=False, choices=['bed', 'wig'], help="output format [bed]")
    return parser.parse_args()

def fileWriter (line, fileHandle):
    fileHandle.write(str(line) + "\n")
    return

def checkCount(windowCount, conversionFactor):
    if windowCount < 1:
        windowCount = 0.001
    return windowCount * conversionFactor


def main():
    args = get_args()

    fileE = args.file1
    fileG = args.file2

    fileHandle = sys.stdout

    if args.out:
        fileHandle = open(args.out,"w")

    sumE = 0
    sumG = 0
    lineNo = 0
    data = {}
    try:
        with open(fileE) as f1, open(fileG) as f2:
            for lineE, lineG in itertools.izip(f1, f2):
                lineNo += 1
                chromE, startE, endE, valE = lineE.rstrip().split('\t')
                chromG, startG, endG, valG = lineG.rstrip().split('\t')
                if ((chromE != chromG) or (startE != startG) or (endE != endG)):
                    raise SystemExit("There is a mismatch between file1 and file2\nFile1:{chrom1}\t{start1}\t{end1}\nFile2:{chrom2}\t{start2}\t{end2}\n".format(chrom1=chromE,start1=startE,end1=endE,chrom2=chromG,start2=startG,end2=endE))
                sumE += int(float(valE))
                sumG += int(float(valG))
                if chromE in data.keys():
                    data[chromE][int(startE)] = {"chrom":chromE, "start":startE, "end":endE, "valE":int(float(valE)), "valG":int(float(valG))}
                else:
                    data[chromE] = {}
                    data[chromE][int(startE)] = {"chrom":chromE, "start":startE, "end":endE, "valE":int(float(valE)), "valG":int(float(valG))}
        f1.close()
        f2.close()
    except IOError as e:
        raise SystemExit("ERROR: Cannot open file: '{0}: {1}'\n".format(e.strerror, e.filename))
    except:
        raise SystemExit ("ERROR: There is a mismatch between file1 and file2 at line {line}\nFile1:{chrom1}\t{start1}\t{end1}\nFile2:{chrom2}\t{start2}\t{end2}\n".format(line=lineNo,chrom1=chromE,start1=startE,end1=endE,chrom2=chromG,start2=startG,end2=endE))

    try:
        gConversionFactor = 1 if not args.noNormalise else sumE/sumG
    except ZeroDivisionError as detail:
        raise SystemExit('ERROR: there is a problem calculating gConversion factor:%s\n' % detail)

    for chromosome, chrData in data.items():
        if args.format == 'wig':
            firstEntry = chrData.keys()[0]
            windowSize = int(chrData[firstEntry]['end']) - int(chrData[firstEntry]['start'])
            print(windowSize)
            headerLine = "fixedStep  chrom={0}  start=1  step={1}  span={2}".format(chromosome, windowSize, windowSize-1)
            fileWriter(headerLine, fileHandle)
        for window, windowData in sorted(chrData.items()):
            countsE = checkCount(windowData['valE'],1)
            countsG = checkCount(windowData['valG'],gConversionFactor)

            try:
                ratio = countsE/countsG
            except ZeroDivisionError:
                raise SystemExit('ERROR: Ratio for window {0}:{1}-{2} could not be computed. Attempted calculation was countsE/countsG.')

            if args.format == 'wig':
                line = '{:4.5f}'.format(ratio)
                fileWriter(line, fileHandle)
            elif args.format == 'bed':
                line = '{chrom}\t{start}\t{end}\t{ratio:4.5f}'.format(chrom=windowData['chrom'], start=windowData['start'], end=windowData['end'], ratio=ratio)
                fileWriter(line, fileHandle)


    if args.out:
        fileHandle.close()

if __name__ == '__main__':
    main()
