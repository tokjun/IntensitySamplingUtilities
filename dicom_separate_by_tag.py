#!/usr/bin/env python3

import os
import sys
import os.path
import argparse
import shutil
import copy

import pydicom
from pydicom.data import get_testdata_files


#
# Match DICOM attriburtes
#
def getDICOMAttribute(path, tag):

    dataset = None
    try:
        dataset = pydicom.dcmread(path, specific_tags=None)
    except pydicom.errors.InvalidDicomError:
        print("Error: Invalid DICOM file: " + path)
        return None
    
    key = tag.replace(',', '')
    if key in dataset:
        element = dataset[tag.replace(',', '')]
        return element.value
    else:
        return None

#
# Convert attribute to folder name (Remove special characters that cannot be
# included in a path name)
#
def removeSpecialCharacter(v):

    input = str(v) # Make sure that the input parameter is a 'str' type.
    removed = input.translate ({ord(c): "-" for c in "!@#$%^&*()[]{};:/<>?\|`="})

    return removed

#
# Load dictionary file.
#

def loadDirectoryNames(filename):
    d = {}
    with open(filename) as f:
        for line in f:
            (key, val) = line.split()
            d[key] = val

    return d


#
# extract DICOM files by Tag, and return the list of attributes ( = names of subfoders)
#
def extractDICOMByTag(srcDir, dstDir, tagList, fRecursive, fMove, dirDict, fPreserve):

    postfix = 0
    attrList = []

    tag = ''

    ## Duplicate the tagList
    tags = copy.copy(tagList)
    if tags:
        tag = tags.pop(0)
    else:
        return

    print("Processing directory: %s..." % srcDir)
    
    for root, dirs, files in os.walk(srcDir):
        for file in files:
            srcFilePath = os.path.join(root, file)
          
            attr = str(getDICOMAttribute(srcFilePath, tag))
            if attr == None:
                print("The image does not contain tag: %s" % tag)
                continue
            newFolderName = removeSpecialCharacter(str(attr))
            if dirDict:
                if attr in dirDict:
                    newFolderName = dirDict[attr]
                    
            dstFilePath=''
            dstSubDirPath=''
            if fPreserve:
                # Preserve the input folder structure, (when used with the recursive option)
                relPath = os.path.relpath(root, srcDir)
                dstSubDirPath = os.path.join(dstDir, relPath)
                dstSubDirPath = os.path.join(dstSubDirPath, newFolderName)
                dstFilePath = os.path.join(dstSubDirPath, file)
            else:
                # Use a flat folder structure under the destinatio folder
                dstSubDirPath= os.path.join(dstDir, newFolderName)
                dstFilePath = os.path.join(dstSubDirPath, file)

            ## Add the attribute to the tag list
            if not (attr in attrList):
                attrList.append(attr)

            ## Create the destination folder, if it does not exist.
            os.makedirs(dstSubDirPath, exist_ok=True)
            
            if os.path.exists(dstFilePath):
                filename, file_extension = os.path.splitext(file)
                newfilename = filename + '_%04d' % postfix + file_extension
                postfix = postfix + 1
                dstFilePath = os.path.join(dstSubDirPath, newfilename)
            if fMove:
                print("Moving: %s -> %s" % (srcFilePath, dstFilePath))
                shutil.move(srcFilePath, dstFilePath)
            else:
                print("Copying: %s -> %s" % (srcFilePath, dstFilePath))
                shutil.copy(srcFilePath, dstFilePath)
                
        if fRecursive == False:
            break

    # Call extractDICOMByTag() recursively
    # (NOTE: the fRecursive flag is for searching the source directory, and does not
    #  affect the call of extractDICOMByTag().)
    for attr in attrList:
        newDirName = removeSpecialCharacter(attr)
        newSrcDir= os.path.join(dstDir, newDirName)
        newDstDir= os.path.join(dstDir, newDirName)
        extractDICOMByTag(newSrcDir, newDstDir, tags, fRecursive, True, dirDict, fRecursive)

        
def main():
    
    parser = argparse.ArgumentParser(description='Extract DICOM files based on tags')
    parser.add_argument('tags', metavar='TAG', type=str, nargs='+',
                        help='DICOM tags(e.g. "0020,000E")')
    parser.add_argument('src', metavar='SRC_DIR', type=str, nargs=1,
                        help='source directory')
    parser.add_argument('dst', metavar='DST_DIR', type=str, nargs=1,
                        help='destination directory')
    parser.add_argument('-r', dest='recursive', action='store_const',
                        const=True, default=False,
                        help='search the source directory recursively')
    parser.add_argument('-p', dest='preserve', action='store_const',
                        const=True, default=False,
                        help=' preserve the input folder structure (should be used with -r)')
    parser.add_argument('-M', dest='move', action='store_const',
                        const=True, default=False,
                        help='move file instead of copying')
    parser.add_argument('-d', dest='dic', default=None, help='dictionary for directory names (in a space-separated-variables file)')

    args = parser.parse_args()
    srcdir = args.src
    dstdir = args.dst
    tagDict = {}
    dirDictFile = args.dic
    dirDict = None

    # Load dictionary file
    if dirDictFile:
        dirDict = loadDirectoryNames(dirDictFile)
    
    # Make the destination directory, if it does not exists.
    os.makedirs(dstdir[0], exist_ok=True)

    extractDICOMByTag(srcdir[0], dstdir[0], args.tags, args.recursive, args.move, dirDict, args.preserve)

        

if __name__ == "__main__":
    main()


