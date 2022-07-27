# IntensitySamplingUtilities
Python scripts to analyze image intensities.


## Usage (Example)

First, extract only the real images in the DICOM folder and copy them to DICOM_IR (Assuming that the DICOM files for the real images set (0051,1016) = "R/DIS2D"); the DICOM tag to flag real/imagnary/phase data depends on systems/sequences)

~~~~
$ dicom_list_by_tag.py -r 00511016=R\/DIS2D DICOM DICOM_IR
~~~~

Then, convert the DICOM files to NRRD files using `dicom_to_nrrd.py`. Users can list DICOM tags they want to include in the file names. The following example converts the DICOM files in the "DICOM_IR" directory to NRRD files, names them with the series number (0020,0011), inversion time (0018,0082), real/imaginary (0051,1016), and series description (0008,103e), and copies them into the "NRRD_IR" directory.

~~~~
$ dicom_to_nrrd.py -r 00200011 00180082 00511016 0008103e DICOM_IR NRRD_IR
~~~~

Using a medical image analysis software, such as 3D Slicer, to define ROIs on the image and save them as a label map in the NRRD format. The label map should be saved in the same directory ("NRRD_IR").

To sample intensities, create an image list file in the JSON format. The image list file lists the images to be sampled and parameters (e.g., IR) associated with the images. The image list file would look like:
~~~~
{
    "label" : "Segmentation-label.nrrd",
    "330"   : "78-330-R.DIS2D-TSE_T1_map TI=330 12 SLICES_RR.nrrd",
    "817"   : "79-817-R.DIS2D-TSE_T1_map TI=817 12 SLICES_RR.nrrd",
    "1490"  : "80-1490-R.DIS2D-TSE_T1_map TI=1490 12 SLICES_RR.nrrd",
    "133"   : "81-133-R.DIS2D-TSE_T1_map TI=133 12 SLICES_RR.nrrd",
    "2730"  : "82-2730-R.DIS2D-TSE_T1_map TI=2730 12 SLICES_RR.nrrd",
    "605"   : "83-605-R.DIS2D-TSE_T1_map TI=605 12 SLICES_RR.nrrd",
    "243"   : "84-243-R.DIS2D-TSE_T1_map TI=243 12 SLICES_RR.nrrd",
    "1100"  : "85-1100-R.DIS2D-TSE_T1_map TI=1100 12 SLICES_RR.nrrd",
    "447"   : "86-447-R.DIS2D-TSE_T1_map TI=447 12 SLICES_RR.nrrd",
    "3670"  : "87-3670-R.DIS2D-TSE_T1_map TI=3670 12 SLICES_RR.nrrd"
}
~~~~

"label" is a special key to define a specify a label map. To sample the intensities in each ROI based on the image list file "list_file.json" and record them in "intensities.csv", run:

~~~~
$ sample_intensities.py list_file.json NRRD_IR intensities.csv
~~~~

