import vtk
import vtk.util.numpy_support as VN
import numpy as np
import os.path

# Choose scalar value to plot. 
# You can choose from 'v02', 'v03', 'prs' and 'tev'.
# scalar_value = 'v02'
scalars = ['v02', 'v03', 'tev']
opacities = [0.5, 0.8, 0.5]

# Download this data yourself! It's not uploaded to Git.
# Download from # http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/ 
filename = 'pv_insitu_300x300x300_41035.vti'

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
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renWin)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    aRenderer.SetBackground(140/255, 140/255, 160/255)

    # Window size of final png file
    renWin.SetSize(650, 650)

    for scalar_value, opacity in zip(scalars, opacities):
        # data reader
        reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(filename)
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
        hueLut.SetHueRange(0.08, 0.98)
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
        opacityTransferFunction.AddPoint(dMin+2*(dMax-dMin)/10, 0)

        # Create transfer mapping scalar value to color.
        colorTransferFunction = vtk.vtkColorTransferFunction()
        colorTransferFunction.SetColorSpaceToDiverging()
        # colorTransferFunction.SetHSVWrap(False)
        if scalar_value == "tev":
            colorTransferFunction.AddRGBPoint(dMin, 0.03, 0.198, 0.85)
            colorTransferFunction.AddRGBPoint(dMax, 0.7, 0.02, 0.15)
        elif scalar_value == "v03":
            colorTransferFunction.AddRGBPoint(dMin, 0, 1, 0)
            colorTransferFunction.AddRGBPoint(dMax, 0.5, 0, 0.5)
        elif scalar_value == "v02":
            colorTransferFunction.AddRGBPoint(dMin, 0.9, 0.898, 0.85)
            colorTransferFunction.AddRGBPoint(dMax, 0.01, 0.02, 0.05)

        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(dMin, 0)
        volumeGradientOpacity.AddPoint(dMin+(dMax-dMin)*0.7,  opacity)
        volumeGradientOpacity.AddPoint(dMax, 1.0)

        # Create volume property (used for volume variable)
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.ShadeOff()
        volumeProperty.SetColor(colorTransferFunction)
        volumeProperty.SetScalarOpacity(opacityTransferFunction)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()

        # Render data
        # TODO: volgens mij maakt het niet uit welke mapper je kiest
        if scalar_value == "v02" or scalar_value == "tev":
            volumeMapper = vtk.vtkSmartVolumeMapper()
        else:
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

    # Render interactive window!
    renWin.Render()
    interactor.Initialize()
    interactor.Start()

    # Screenshot when hide interactive mode
    # Comment this section if you do not want to save the file to png
    # w2if = vtk.vtkWindowToImageFilter()
    # w2if.SetInput(renWin)
    # w2if.Update()

    # outputFile = outputDir+"/"+str(index)+".png"

    # writer = vtk.vtkPNGWriter()
    # writer.SetFileName(outputFile)
    # writer.SetInputConnection(w2if.GetOutputPort())
    # writer.Write()



if __name__ == '__main__':
    createImage(filename)
