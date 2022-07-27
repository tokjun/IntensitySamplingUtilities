#!/usr/bin/env python3

import os
import sys
import os.path
import argparse
import shutil

import pydicom
from pydicom.data import get_testdata_files


#
# Match DICOM attriburtes
#
def matchDICOMAttributes(path, tagDict, match):

    # When match == True, the attributes must match the dictionary value.
    # When match == False, the attributes only need to contain the dictionary values
    dataset = pydicom.dcmread(path, specific_tags=None)
    for tag in tagDict:
        if tag in dataset:
            element = dataset[tag]
            strs = tagDict[tag]
            if match:
                for s in strs:
                    if s == str(element.value):
                        return True
            else:
                for s in strs:
                    if s in str(element.value):
                        return True
    return False


def main():
    
    parser = argparse.ArgumentParser(description='List DICOM files based on tags')
    parser.add_argument('tags', metavar='TAG', type=str, nargs='+',
                        help='Pairs of DICOM tags and attributes separated by "=" (e.g. "0020,000E=3" means "if the series number is 3")')
    parser.add_argument('src', metavar='SRC_DIR', type=str, nargs=1,
                        help='source directory')
    parser.add_argument('dst', metavar='DST_DIR', type=str, nargs=1,
                        help='destination directory')
    parser.add_argument('-r', dest='recursive', action='store_const',
                        const=True, default=False,
                        help='search the source directory recursively')
    parser.add_argument('-m', dest='match', action='store_const',
                        const=True, default=False,
                        help='attributes must exactly match')
    parser.add_argument('-M', dest='move', action='store_const',
                        const=True, default=False,
                        help='move file instead of copying')


    args = parser.parse_args()
    srcdir = args.src
    dstdir = args.dst
    tagDict = {}

    # Make the destination directory, if it does not exists.
    os.makedirs(dstdir[0], exist_ok=True)

    # Convert tags (e.g. "0020,000E=XXX") to dictionary ( {0x0020000E: XXXX})
    for tag in args.tags:
        pair = tag.split('=')
        if len(pair) != 2:
            sys.exit('ERROR: Invalid argument: %s' % tag)
        tagHexStr = '0x' + pair[0].replace(',', '')
        tagNum = int(tagHexStr, 16)
        if tagNum in tagDict:
            tagDict[tagNum] = tagDict[tagNum] + (pair[1],)
        else:
            tagDict[tagNum] = (pair[1],)

    postfix = 0
    for root, dirs, files in os.walk(srcdir[0]):
        for file in files:
            filepath = os.path.join(root, file)
            if matchDICOMAttributes(filepath, tagDict, args.match):
                newfilepath = os.path.join(dstdir[0], file)
                dstfilepath = ''
                if os.path.exists(newfilepath):
                    filename, file_extension = os.path.splitext(file)
                    newfilename = filename + '_%04d' % postfix + file_extension
                    postfix = postfix + 1
                    dstfilepath = os.path.join(dstdir[0], newfilename)
                else:
                    dstfilepath = os.path.join(dstdir[0], file)
                if args.move:
                    print("Moving: %s" % filepath)
                    shutil.move(filepath, dstfilepath)
                else:
                    print("Copying: %s" % filepath)
                    shutil.copy(filepath, dstfilepath)
                
        if args.recursive == False:
            break
    
if __name__ == "__main__":
    main()
