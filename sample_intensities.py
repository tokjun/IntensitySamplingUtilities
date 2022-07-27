#
# Script to sample intensity values in ROIs defined by a label map
# 
# Usage: On the Slicer's Python interactor, 
#
#   >>> execfile('/path/to/script/IntensitySampling.py')
# or, if execfile() is not available,
#   >>> exec(open('/path/to/script/IntensitySampling.py').read())
# then
#   >>> IntensitySampling(imageListFile, sourceDir, outputFile)
#      
# Arguements:
#
#   'imageListFile'
#      The path to a file that contains the list of input image files.
#      The first line must be the name of the label map, whereas the rest
#      are the names of image files to be sampled. One file per line.
#
#   'sourceDir'
#      The path to the folder that contains the image files.
#
#   'outputFile'
#      The path to the output file.
#

import argparse, sys, shutil, os, logging
import numpy
import re
import SimpleITK as sitk
import json


def sampleIntensity(imageListFile, sourceDir, outputFile):
    
    ### Open output file
    outputFile = open(outputFile, 'w')
    outputFile.write("Param,Index,Count,Min,Max,Mean,StdDev\n")

    ### Load the image file dictionary
    imageDict = None
    with open(imageListFile, "r") as read_file:
        imageDict = json.load(read_file)
        
    ### Load the label map
    if 'label' in imageDict:
        path = sourceDir + '/' + imageDict['label']
        roiImage = sitk.ReadImage(path, sitk.sitkInt8)
        # Remove the label map from the dictionary
        del imageDict['label']
    else:
        print("ERROR: No label map is specified in the ")
        return 0

    ### Get a list of parameters (i.e., TI) and sort
    params = list(imageDict.keys())        # This is a string array
    print (params)
    params_num = [float(x) for x in params]  # Convert to a numeric array
    params_num, params = zip (*sorted(zip(params_num,params))) # Sort by params_num
    params = list(params)
    print (params)

    for param in params:
        path = sourceDir + '/' + imageDict[param]
        image = sitk.ReadImage(path, sitk.sitkInt16)
        
        labelStatistics = sitk.LabelStatisticsImageFilter()
        labelStatistics.Execute(image, roiImage)
            
        n = labelStatistics.GetNumberOfLabels()
        
        for i in range(1,n):
            outputFile.write("%s," % param)                         # Param (i.e., TI, Time, ..)
            outputFile.write("%d," % i)                             # Index
            outputFile.write("%f," % labelStatistics.GetCount(i))   # Count
            outputFile.write("%f," % labelStatistics.GetMinimum(i)) # Min
            outputFile.write("%f," % labelStatistics.GetMaximum(i)) # Max
            outputFile.write("%f," % labelStatistics.GetMean(i))    # Mean
            outputFile.write("%f\n"% labelStatistics.GetSigma(i))   # StdDev

            
def main(argv):
    
    try:
        parser = argparse.ArgumentParser(description="Split DICOM series by Tag.")
        parser.add_argument('flist', metavar='LIST_FILE', type=str, nargs=1,
                            help='Image list file (in the JSON format)')
        parser.add_argument('src', metavar='SRC_DIR', type=str, nargs=1,
                            help='Source directory')
        parser.add_argument('out', metavar='OUTPUT_FILE', type=str, nargs=1,
                            help='Output file')
        args = parser.parse_args(argv)

    except Exception as e:
        print(e)

    listfile = args.flist[0]
    srcdir = args.src[0]
    outfile = args.out[0]

    sampleIntensity(listfile, srcdir, outfile)
    
    sys.exit()

if __name__ == "__main__":
  main(sys.argv[1:])

