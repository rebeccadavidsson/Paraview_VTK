import vtk
import vtk.util.numpy_support as VN
import numpy as np
import os.path
from tqdm import tqdm
from PIL import Image
import csv
import pickle
from helpers import createGif, createCSV, getInfo

# Define the render method
method = 'volume'

# Output folder of images
outputDir = "cvlibd/server/data/volume-render/images"
prs_outputDir = "cvlibd/server/data/volume-render/prs_images"


if not os.path.isdir(outputDir):
    os.makedirs(outputDir)

if not os.path.isdir(prs_outputDir):
    os.makedirs(prs_outputDir)


def createImage(directory, outputDir, filename, scalars, opacities, interactiveWindow=False,
                savePickle=False, loadFromPickle=False):
    """
    Create a .png image for a given .vti file, using
    three scalars and VolumeRendering. Opacities have to be
    specified for the scalars.
    Colors-schemes are hardcoded... :-)
    """

    colors = vtk.vtkNamedColors()
    aRenderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(aRenderer)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renWin)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    aRenderer.SetBackground(15/255, 15/255, 25/255)

    # Window size of final png file
    renWin.SetSize(650, 650)

    for scalar_value, opacity in zip(scalars, opacities):
        # data reader
        reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(directory + "/" + filename)
        reader.Update()

        # Set scalar_value
        reader.GetOutput().GetPointData().SetActiveAttribute(scalar_value, 0)

        # Get the min and maximum value from the array of points.
        # This is a flat array, but can be reshaped to a (300x300x300) array
        dary = VN.vtk_to_numpy(
            reader.GetOutput().GetPointData().GetScalars(scalar_value))
        if savePickle:
            pickle.open(dary, open('pickle/' + filename, 'wb'))

        dMax = np.amax(dary)
        dMin = np.amin(dary)

        # Coloring
        hueLut = vtk.vtkLookupTable()
        hueLut.SetTableRange(dMin, dMax)
        hueLut.SetHueRange(0, 1)
        hueLut.SetRampToLinear()
        hueLut.SetSaturationRange(0, 1)
        # hueLut.SetValueRange(1, 1)
        hueLut.SetTableValue(dMin, 255/255, 255/255, 212/255)
        hueLut.SetTableValue(dMax, 255/255, 10/255, 1/255)
        hueLut.Build()

        # An outline provides context around the data.
        outlineData = vtk.vtkOutlineFilter()
        outlineData.SetInputConnection(reader.GetOutputPort())
        outlineData.Update()

        mapOutline = vtk.vtkPolyDataMapper()
        mapOutline.SetInputConnection(outlineData.GetOutputPort())

        outline = vtk.vtkActor()
        outline.SetMapper(mapOutline)
        outline.GetProperty().SetColor(colors.GetColor3d("Black"))

        # Volume rendering
        # Create transfer mapping scalar value to opacity.
        opacityTransferFunction = vtk.vtkPiecewiseFunction()
        opacityTransferFunction.AddPoint(dMin, 0.0)
        opacityTransferFunction.AddPoint(dMax, opacity)
        # opacityTransferFunction.AddPoint(dMin+2*(dMax-dMin), opacity)
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(dMin, 0)
        # volumeGradientOpacity.AddPoint(dMax, 0.1)

        # Create transfer mapping scalar value to color.
        colorTransferFunction = vtk.vtkColorTransferFunction()
        colorTransferFunction.SetColorSpaceToDiverging()
        # colorTransferFunction.SetHSVWrap(False)
        if scalar_value == "tev":
            volumeGradientOpacity.AddPoint(dMax/2, opacity)
            colorTransferFunction.AddRGBPoint(dMin, 255/255, 255/255, 212/255) # light yellow
            colorTransferFunction.AddRGBPoint((dMax + dMin)/5, 254/255, 227/255, 145/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin)/4, 254/255,196/255,79/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin)/3, 254/255, 153/255, 41/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin)/2, 217/255, 95/255, 14/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin), 163/255,62/255,4/255)
        elif scalar_value == "v03":
            colorTransferFunction.AddRGBPoint(dMax/3, 76/255, 0/255, 123/255) # Green
            colorTransferFunction.AddRGBPoint(dMin, 0, 184/255, 92/255)  # Purple
            volumeGradientOpacity.AddPoint(dMax/3, opacity)
        elif scalar_value == "v02":
            volumeGradientOpacity.AddPoint(dMax/2, opacity)
            colorTransferFunction.AddRGBPoint(dMin, 235/255, 235/255, 255/255)  # Very light blue
            colorTransferFunction.AddRGBPoint(dMax, 24/255, 32/255, 205/255)  # Blue
        elif scalar_value == "prs":
            volumeGradientOpacity.AddPoint(dMax, opacity) # Coolwarm (blue to red)
            colorTransferFunction.AddRGBPoint(dMin, 178/255, 24/255, 42/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/7, 239/255, 254/255, 98/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/6, 253/255, 219/255, 199/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/5, 209/255, 229/255, 240/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/4, 103/255, 169/255, 207/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/3, 33/255, 102/255, 172/255)


        # Create volume property (used for volume variable)
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.ShadeOff()
        volumeProperty.SetColor(colorTransferFunction)
        volumeProperty.SetScalarOpacity(opacityTransferFunction)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()

        # Render data
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(reader.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()

        # Position/orient volume
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)
        aRenderer.AddActor(volume)
    

    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 1, 0)
    aCamera.SetPosition(0, 0, 1) 
    if "prs" in scalars:
        aCamera.SetFocalPoint(0.7, 0, 0.3)
    else:
        aCamera.SetFocalPoint(0.6, 0.2, 0)
    aCamera.ComputeViewPlaneNormal()

    # Camera views
    aRenderer.SetActiveCamera(aCamera)
    aRenderer.ResetCamera()

    # Zooming in
    aCamera.Dolly(1.2)

    # Stand van camera
    aCamera.Elevation(13)
    aRenderer.ResetCameraClippingRange()
    renWin.Render()

    # Render interactive window!
    if interactiveWindow:
        interactor.Initialize()
        interactor.Start()
    else:
        # Screenshot when not in interactive mode
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(renWin)
        w2if.Update()

        if "prs" in scalars:
            outputFile = outputDir+"/"+str(filename) + "prs.png"
        else:
            outputFile = outputDir+"/"+str(filename) + ".png"

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(outputFile)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()


def createImages(directory, outputDir, scalars, opacities, interactiveWindow):
    """
    Find all files with .vti extension and convert them
    to .png using the createImage function.
    It checks first if this file has not been converted before.
    """

    already_converted = os.listdir(outputDir)
    not_converted = []

    for filename in os.listdir(directory):
        if "prs" in scalars:
            if filename.endswith(".vti") and filename + "prs.png" not in already_converted:
                not_converted.append(filename)
        elif filename.endswith(".vti") and filename + ".png" not in already_converted:
            not_converted.append(filename)

    if len(not_converted) > 0:
        print("Start converting", len(not_converted), "images")
        for i in tqdm(not_converted):
            createImage(directory, outputDir, i, scalars, opacities, interactiveWindow=False)
    return True


if __name__ == '__main__':

    # Convert data to csv for plotting
    # getInfo('data')
    # exit()

    # Test image with one file
    # createImage('data', "pv_insitu_300x300x300_22010.vti", interactiveWindow=True)

    # Download this data yourself! It's not uploaded to Git.
    # Download from http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/
    # Specify the folder name where data is stored
    # This function finds all .vti data and converts it to a .png


    # Choose scalar value to plot.
    # You can choose from 'v02', 'v03', 'prs' and 'tev'.
    print("Creating images")
    scalars = ['v02', 'v03', 'tev']
    opacities = [0.1, 0.3, 0.1]
    createImages('data', outputDir, scalars, opacities, interactiveWindow=False)

    # print("Creating pressure images")
    scalars = ['prs']
    opacities = [0.7]
    createImages('data', prs_outputDir, scalars, opacities, interactiveWindow=False)

    # Choose to comment function out or not
    createGif(outputDir, "GIFS/allscalars")
    createGif(prs_outputDir, "GIFS/prs")

    # Call this function in order to write the filenames to csv,
    # only used for the HTML-representation.
    createCSV(outputDir, "cvlibd/server/data/volume-render/data.csv",
              output_type="scalars")
    createCSV(prs_outputDir,
              "cvlibd/server/data/volume-render/data_prs.csv", output_type="prs")

