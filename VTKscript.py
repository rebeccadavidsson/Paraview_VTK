import vtk
import vtk.util.numpy_support as VN
import numpy as np
import os.path
from tqdm import tqdm
from PIL import Image
import csv

# Choose scalar value to plot. 
# You can choose from 'v02', 'v03', 'prs' and 'tev'.
scalars = ['v02', 'v03', 'tev']
opacities = [0.05, 1, 0.1]

# Define the render method
method = 'volume'

# Output folder of images
outputDir = "cvlibd/server/data/volume-render/images"


if not os.path.isdir(outputDir):
    os.makedirs(outputDir)


def createImage(directory, filename):
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

        # Get the min and maximum valule
        dary = VN.vtk_to_numpy(
            reader.GetOutput().GetPointData().GetScalars(scalar_value))
        dMax = np.amax(dary)
        dMin = np.amin(dary)

        # Coloring
        hueLut = vtk.vtkLookupTable()
        hueLut.SetTableRange(dMin, dMax)
        # hueLut.SetHueRange(0, 1)
        # hueLut.SetSaturationRange(0, 1)
        hueLut.SetValueRange(1, 1)
        hueLut.SetTableValue(dMin, 255/255, 255/255, 212/255)
        hueLut.SetTableValue(dMax, 255/255, 10/255, 1/255)
        hueLut.Build()

        # create the color bar legend
        scalar_bar = vtk.vtkScalarBarActor()
        scalar_bar.SetOrientationToVertical()
        scalar_bar.UseOpacityOn()
        scalar_bar.SetLookupTable(hueLut)
        scalar_bar.SetTitle(scalar_value)

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
            colorTransferFunction.AddRGBPoint((dMax + dMin), 153/255,52/255,4/255)
        elif scalar_value == "v03":
            colorTransferFunction.AddRGBPoint(dMax/3, 76/255, 0/255, 153/255) # Green
            colorTransferFunction.AddRGBPoint(dMin, 0, 204/255, 102/255)  # Purple
            volumeGradientOpacity.AddPoint(dMax/3, opacity)
        elif scalar_value == "v02":
            volumeGradientOpacity.AddPoint(dMax/2, opacity)
            colorTransferFunction.AddRGBPoint(dMin, 235/255, 235/255, 255/255)  # Very light blue
            colorTransferFunction.AddRGBPoint(dMax, 24/255, 32/255, 255/255)  # Blue



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
    

    # create the scalar_bar_widget
    # scalar_bar_widget = vtk.vtkScalarBarWidget()
    # scalar_bar_widget.SetInteractor(interactor)
    # scalar_bar_widget.SetScalarBarActor(scalar_bar)
    # scalar_bar_widget.On()
    
    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 1, 0)
    aCamera.SetPosition(0, 0, 1) 
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

    # Render interactive window!
    renWin.Render()
    # interactor.Initialize()
    # interactor.Start()

    # Screenshot when hide interactive mode
    # Comment this section if you do not want to save the file to png
    #________________________________________________________________
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    outputFile = outputDir+"/"+str(filename)+".png"

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(outputFile)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()
    #________________________________________________________________


def createImages(directory):
    """
    Find all files with .vti extension and convert them
    to .png using the createImage function.
    It checks first if this file has not been converted before.
    """

    already_converted = os.listdir(outputDir)
    not_converted = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".vti") and filename + ".png" not in already_converted:
            not_converted.append(filename)
        else:
            continue

    if len(not_converted) > 0:
        print("Start converting", len(not_converted), "images")
        for i in tqdm(not_converted):
            createImage(directory, i)
    return True


def createGif(outputDir):
    """
    Returns a GIF from .png files in a given directory
    """
    print("Creating GIF")
    images = os.listdir(outputDir)
    images.sort()
    images = [Image.open(outputDir + '/' + i).convert('RGBA').quantize()
              for i in images if i.endswith('.png')]

    images[0].save('volume.gif', 
                   optimize=False, 
                   duration=500,  
                   save_all=True,
                   interlace=False,
                   append_images=images[1:])


def createCSV(outputDir, outputFile):
    images = os.listdir(outputDir)
    images.sort()

    # Add folder name
    images = ["images/" + image for image in images]
        
    indexes = list(range(1, len(images) + 1))
    f = open(outputFile, 'w')

    with f:
        writer = csv.writer(f)
        writer.writerow(["Value", "image"])
        for row in zip(indexes, images):
            writer.writerow(row)
            

if __name__ == '__main__':
    # Download this data yourself! It's not uploaded to Git.
    # Download from http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/
    # Specify the folder name where data is stored
    # This function finds all .vti data and converts it to a .png
    createImages('data')

    # createGif(outputDir)

    # Call this function in order to write the filenames to csv,
    # only used for the HTML-representation.
    createCSV(outputDir, "cvlibd/server/data/volume-render/data.csv")
