from numpy import unravel_index
import os
import vtk
import numpy as np
import vtk.util.numpy_support as VN
import csv
from PIL import Image
import re



def createGif(outputDir, filename):
    """
    Returns a GIF from .png files in a given directory
    """
    print("Creating GIF")
    images = os.listdir(outputDir)
    images.sort()
    images = [Image.open(outputDir + '/' + i).convert('RGBA').quantize()
              for i in images if i.endswith('.png')]

    images[0].save(filename + '.gif',
                   optimize=False,
                   duration=250,
                   save_all=True,
                   interlace=False,
                   append_images=images[1:],
                   loop=10)

def createGif_slices(outputDir, filename):
    """
    Returns a GIF from .png files in a given directory for sliced images
    """
    print("Creating GIF")
    images = os.listdir(outputDir)
    if ".DS_Store" in images:
        images.remove(".DS_Store")
        
    total = []
    for i in images:
        total.append(int(i.replace('.0.png', "")))
    images = total
    images.sort()
    images = [Image.open(outputDir + '/' + str(i) + '.0.png').convert('RGBA').quantize()
              for i in images]

    images[0].save(filename + '.gif',
                   optimize=False,
                   duration=50,
                   save_all=True,
                   interlace=False,
                   append_images=images[1:],
                   loop=10)

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def createCSV(outputDir, outputFile, num_yValues, num_xValues, output_type):
    """
    Create CSV file of the data stored in the array, extracted from
    the vti file using 'VN.vtk_to_numpy()'.
    """
    images = os.listdir(outputDir)
    images.sort(key=natural_keys)
    if ".DS_Store" in images:
        images.remove(".DS_Store")

    # Add folder name
    if output_type == "prs":
        images = ["prs_images/" + image for image in images]
    else:
        images = ["tev_images/" + image for image in images]

    # indexes = list(range(1, len(images) + 1))
    f = open(outputFile, 'w')

    with f:
        writer = csv.writer(f)
        writer.writerow(["phi", "theta", "Value", "image"])

        yValue, xValue, val = 0, 0, 0
        for i in range(len(images)):

            writer.writerow([yValue, xValue, val, images[i]])
            
            xValue += 1
           

            # Range between 0 and 5
            xValue = xValue % (num_xValues)

            # Go to next yValue
            # print(i % num_xValues == 0)
            if i <= num_xValues:
                if i % (num_xValues - 1) == 0 and i != 0:
                    yValue += 1
            else:
                if i % (num_xValues) == num_xValues - 1:
                    yValue += 1
        
            # Range between 0 and 2
            yValue = yValue % (num_yValues)

            if i <= (num_xValues * num_yValues):
                if i % (num_xValues * num_yValues - 1) == 0 and i != 0:
                    val += 1
            else:
                if i % (num_xValues * num_yValues) == num_xValues * num_yValues - 1:
                    val += 1



def getInfo(directory):
    temperatures, v02, v03, pressures, rho = [], [], [], [], []
    temperatures_max, v02_max, v03_max, pressures_max, rho_max = [], [], [], [], []
    combined = [temperatures, v02, v03, pressures, rho, 
                temperatures_max, v02_max, v03_max, pressures_max, rho_max]
    scalar_values = ["tev", "v03", "prs", "rho", "tev", "v03", "prs", "rho"]
    filenames = os.listdir(directory)
    filenames.sort()

    for filename in filenames:
        if filename.endswith(".vti"):
            reader = vtk.vtkXMLImageDataReader()
            reader.SetFileName(directory + "/" + filename)
            reader.Update()
            for scalar_value, list_name in zip(scalar_values, combined):
                try:
                    reader.GetOutput().GetPointData().SetActiveAttribute(scalar_value, 0)
                    dary = VN.vtk_to_numpy(
                        reader.GetOutput().GetPointData().GetScalars(scalar_value))
                except:
                    list_name.append("")

                list_name.append(np.max(dary))


    for scalar_value, list_name in zip(scalar_values, combined):
        indexes = list(range(1, len(list_name) + 1))
        f = open("cvlibd/server/data/volume-render/" +
                 scalar_value + "_max.csv", 'w')

        with f:
            writer = csv.writer(f)
            writer.writerow(["timestep", scalar_value])
            for row in zip(indexes, list_name):
                writer.writerow(row)

    return True


def calcSplash(directory): 
    v02 = []
    scalar_value = "v02"
    filenames = os.listdir(directory)
    filenames.sort()

    for filename in filenames:
        if filename.endswith(".vti"):
            reader = vtk.vtkXMLImageDataReader()
            reader.SetFileName(directory + "/" + filename)
            reader.Update()

            reader.GetOutput().GetPointData().SetActiveAttribute(scalar_value, 0)
            dary = VN.vtk_to_numpy(
                reader.GetOutput().GetPointData().GetScalars(scalar_value))

            dary = dary.reshape(300, 300, 300)
            dary = np.swapaxes(dary, 0, 1)
            dary = np.flipud(dary)
            v02.append(list(unravel_index(dary.argmax(), dary.shape)))

    indexes = list(range(1, len(v02) + 1))
    f = open("cvlibd/server/data/volume-render/" +
             scalar_value + "_splash.csv", 'w')

    with f:
        writer = csv.writer(f)
        writer.writerow(["timestep", "y", "x", "z"])
        for row, line in zip(indexes, v02):
            writer.writerow([row, line[0], line[1], line[2]])

    return True

