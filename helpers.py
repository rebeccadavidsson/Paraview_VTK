import os
import vtk
import numpy as np
import vtk.util.numpy_support as VN
import csv
from PIL import Image

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
                   duration=500,
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


def createCSV(outputDir, outputFile, output_type):
    """
    Create CSV file of the data stored in the array, extracted from
    the vti file using 'VN.vtk_to_numpy()'.
    """
    images = os.listdir(outputDir)
    images.sort()
    if ".DS_Store" in images:
        images.remove(".DS_Store")
    # Add folder name

    if output_type == "prs":
        images = ["prs_images/" + image for image in images]
    else:
        images = ["images/" + image for image in images]

    indexes = list(range(1, len(images) + 1))
    f = open(outputFile, 'w')

    with f:
        writer = csv.writer(f)
        writer.writerow(["Value", "image"])
        for row in zip(indexes, images):
            writer.writerow(row)


def getInfo(directory):
    temperatures, v02, v03, pressures = [], [], [], []
    combined = [temperatures, v02, v03, pressures]
    scalar_values = ["tev", "v03", "prs"]

    for filename in os.listdir(directory):
        if filename.endswith(".vti"):
            reader = vtk.vtkXMLImageDataReader()
            reader.SetFileName(directory + "/" + filename)
            reader.Update()
            for scalar_value, list_name in zip(scalar_values, combined):
                reader.GetOutput().GetPointData().SetActiveAttribute(scalar_value, 0)
                dary = VN.vtk_to_numpy(
                    reader.GetOutput().GetPointData().GetScalars(scalar_value))
                # dMax = np.amax(dary)
                # dMin = np.amin(dary)
                list_name.append(np.mean(dary))
                print(np.mean(dary))

    for scalar_value, list_name in zip(scalar_values, combined):
        indexes = list(range(1, len(list_name) + 1))
        f = open("cvlibd/server/data/volume-render/" +
                 scalar_value + ".csv", 'w')

        with f:
            writer = csv.writer(f)
            writer.writerow(["timestep", scalar_value])
            for row in zip(indexes, list_name):
                writer.writerow(row)

    return True
