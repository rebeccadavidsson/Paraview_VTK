import vtk
import vtk.util.numpy_support as VN
import numpy as np
import re
from pathlib import Path
from multiprocessing import Pool
import os.path


# Choose scalar value to plot. 
# You can choose from 'v02', 'v03', 'prs' and 'tev'.
scalar_value = 'v02'

# Download this data yourself! It's not uploaded to Git.
# Download from # http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/ 
filename = '49275.vti'

# Define the render method
method = 'volume'

# Output folder of images
outputDir = "output" 

if not os.path.isdir(outputDir):
    os.makedirs(outputDir)


def createImage(index):
    """
    TODO: beschrijving....
    """

    colors = vtk.vtkNamedColors() 
    aRenderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(aRenderer)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    aRenderer.SetBackground(40/255, 40/255, 60/255)

    # Window size of final png file
    renWin.SetSize(550, 550)

    # data reader
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filename)
    reader.Update()

    # Set scalar_value
    reader.GetOutput().GetPointData().SetActiveAttribute(scalar_value, 0)

    # Get the min and maximum valule
    dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars(scalar_value))
    dMax = np.amax(dary)
    dMin = np.amin(dary)

    # Coloring
    hueLut = vtk.vtkLookupTable()
    hueLut.SetTableRange(dMin, dMax)
    hueLut.SetHueRange(0.28, 0.78) 
    hueLut.SetSaturationRange(0, 1)
    hueLut.SetValueRange(1, 1)
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
    opacityTransferFunction.AddPoint(dMax, 1)
    opacityTransferFunction.AddPoint(dMin+2*(dMax-dMin)/3, 0)

    # Create transfer mapping scalar value to color.
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.SetColorSpaceToDiverging()
    # colorTransferFunction.SetHSVWrap(False)
    colorTransferFunction.AddRGBPoint(dMin, 0.23, 0.298, 0.85)
    # colorTransferFunction.AddRGBPoint(dMin+(dMax-dMin)/3, 0.865,0.865,0.865)
    colorTransferFunction.AddRGBPoint(dMax, 0.705, 0.02, 0.15)

    
    volumeGradientOpacity = vtk.vtkPiecewiseFunction()
    volumeGradientOpacity.AddPoint(dMin, 0)
    volumeGradientOpacity.AddPoint(dMin+(dMax-dMin)*0.9,  0.5)
    volumeGradientOpacity.AddPoint(dMax, 1.0)

    # The property describes how the data will look.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)
    volumeProperty.SetGradientOpacity(volumeGradientOpacity)
    volumeProperty.SetInterpolationTypeToLinear()
    # volumeProperty.ShadeOn()

    # The mapper / ray cast function know how to render the data.
    volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
    volumeMapper.SetInputConnection(reader.GetOutputPort())
    volumeMapper.SetBlendModeToComposite()

    # The volume holds the mapper and the property and
    # can be used to position/orient the volume.
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)
    aRenderer.AddActor(volume)

    # Actors are added to the renderer.
    # aRenderer.AddActor(outline)
    # aRenderer.AddActor(timeIndex)

    # It is convenient to create an initial view of the data. The
    # FocalPoint and Position form a vector direction. Later on
    # (ResetCamera() method) this vector is used to position the camera
    # to look at the data in this direction.
    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 1, 0)
    aCamera.SetPosition(0, 0, 1) 
    aCamera.SetFocalPoint(0, 0, 0)
    aCamera.ComputeViewPlaneNormal()


    # Camera views
    aRenderer.SetActiveCamera(aCamera)
    aRenderer.ResetCamera()

    # Zooming in
    aCamera.Dolly(1.2)

    # Stand van camera
    aCamera.Elevation(10)
    aRenderer.ResetCameraClippingRange()

    # Interact with the data.
    renWin.Render()
    iren.Initialize()
    iren.Start()

    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    outputFile = outputDir+"/"+str(index)+".png"

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(outputFile)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()



if __name__ == '__main__':
    createImage(filename)