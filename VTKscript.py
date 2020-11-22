import vtk
import vtk.util.numpy_support as VN
import numpy as np
import os.path
from tqdm import tqdm
from PIL import Image
import csv
import pickle
from helpers import createGif, createCSV, getInfo, createGif_slices, calcSplash

# External disk
# os.chdir('/Volumes/BLACKBOX/Paraview_VTK')



# Download this data yourself! It's not uploaded to Git.
# Download from http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/

# Specify the folder name where data is stored
stored_folder = 'data'

# Define the render method
method = 'volume'

# Output folder of images
outputDir = "cvlibd/server/data/volume-render/tev_images"
prs_outputDir = "cvlibd/server/data/volume-render/prs_images"

num_yValues = 4
num_xValues = 6

# if not os.path.isdir(outputDir):
#     os.makedirs(outputDir)

# if not os.path.isdir(prs_outputDir):
#     os.makedirs(prs_outputDir)


def createImage(directory, outputDir, filename, scalars, opacities, 
                interactiveWindow=False, savePickle=False, 
                loadFromPickle=False, plane=False):
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
    renWin.SetSize(850, 750)

    for scalar_value, opacity in zip(scalars, opacities):

        # data reader
        reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(directory + "/" + filename)
        reader.Update()

        try:
            # Set scalar_value
            reader.GetOutput().GetPointData().SetActiveAttribute(scalar_value, 0)

            # Get the min and maximum value from the array of points.
            # This is a flat array, but can be reshaped to a (300x300x300) array
            dary = VN.vtk_to_numpy(
                reader.GetOutput().GetPointData().GetScalars(scalar_value))
        except AttributeError:
            continue

        dMax = np.amax(dary)
        dMin = np.amin(dary)

        # Coloring
        hueLut = vtk.vtkLookupTable()
        hueLut.SetTableRange(dMin, dMax)
        hueLut.SetHueRange(0, 1)
        hueLut.SetRampToLinear()
        hueLut.SetSaturationRange(0, 1)
        hueLut.SetValueRange(1, 1)
        hueLut.SetTableValue(dMin, 255/255, 255/255, 212/255)
        hueLut.SetTableValue(dMax, 255/255, 10/255, 1/255)
        hueLut.Build()

        # An outline provides context around the data.
        outlineData = vtk.vtkOutlineFilter()
        outlineData.SetInputConnection(reader.GetOutputPort())
        outlineData.Update()

        # Volume rendering
        # Create transfer mapping scalar value to opacity.
        opacityTransferFunction = vtk.vtkPiecewiseFunction()
        opacityTransferFunction.AddPoint(dMin, 0.0)
        opacityTransferFunction.AddPoint(dMax, opacity)
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(dMin, 0)

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
            volumeGradientOpacity.AddPoint(dMax, opacity) # Blue scheme (blue to lightblue)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/1, 3/255, 4/255, 94/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/2, 0, 119/255, 182/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/3, 0, 180/255, 216/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/4, 144/255, 224/255, 239/255)
            colorTransferFunction.AddRGBPoint((dMin + dMax)/5, 202/255, 240/255, 248/255)
            # colorTransferFunction.AddRGBPoint((dMin + dMax)/3, 33/255, 102/255, 172/255)
        elif scalar_value == "rho":
            volumeGradientOpacity.AddPoint(dMax, 1)
            colorTransferFunction.AddRGBPoint((dMin / 6),  237/255, 224/255, 212/255) # light brown to brown
            colorTransferFunction.AddRGBPoint((dMax + dMin)/5,  230/255, 204/255, 178/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin)/4, 221/255, 184/255, 146/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin)/3, 176/255, 137/255, 104/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin)/2, 127/255, 85/255, 57/255)
            colorTransferFunction.AddRGBPoint((dMax + dMin)/1, 156/255, 102/255, 68/255)

            aa_image = vtk.vtkAssignAttribute()
            aa_image.SetInputConnection(reader.GetOutputPort())
            thresh_image = vtk.vtkThreshold()
            thresh_image.SetInputConnection(aa_image.GetOutputPort())
            thresh_image.ThresholdByLower(1/10e-1)
            thresh_image.ThresholdByLower(1/10e-3)
            surface_image = vtk.vtkDataSetSurfaceFilter()
            surface_image.SetInputConnection(thresh_image.GetOutputPort())
            mapper_image = vtk.vtkPolyDataMapper()
            mapper_image.SetInputConnection(surface_image.GetOutputPort())

        mapOutline = vtk.vtkPolyDataMapper()
        mapOutline.SetInputConnection(outlineData.GetOutputPort())
        if scalar_value == "rho":
            outline = vtk.vtkActor()
            outline.SetMapper(mapper_image)
            outline.GetProperty().SetColor(colors.GetColor3d("Black"))
        else:
            outline = vtk.vtkActor()
            outline.SetMapper(mapOutline)
            outline.GetProperty().SetColor(colors.GetColor3d("Black"))


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
    
    camera_pos_y = np.linspace(-0.1, 0.3, num_yValues).tolist()
    camera_pos_x = np.linspace(-0.5, 2.5, num_xValues).tolist()
    i = 0
    for pos_y in camera_pos_y:
        for pos_x in camera_pos_x:
            aCamera = vtk.vtkCamera()
            aCamera.SetViewUp(0, 0, 0)
            aCamera.SetPosition(pos_x, pos_y, 1)
            if "prs" in scalars:
                aCamera.SetFocalPoint(0, 0, 0.3)
            else:
                aCamera.SetFocalPoint(0.6, 0.2, 0)
            aCamera.ComputeViewPlaneNormal()

            # Camera views
            aRenderer.SetActiveCamera(aCamera)
            aRenderer.ResetCamera()

            # Zooming in
            aCamera.Dolly(1)

            # Stand van camera
            aCamera.Elevation(5)
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
                    outputFile = outputDir+"/" + str(filename.replace("pv_insitu_300x300x300_", "")) + "_" + str(i) + ".prs.png"
                else:
                    outputFile = outputDir+"/" + str(filename.replace("pv_insitu_300x300x300_", ""))  + "_" + str(i) +  ".png"

                writer = vtk.vtkPNGWriter()
                writer.SetFileName(outputFile)
                writer.SetInputConnection(w2if.GetOutputPort())
                writer.Write()
            i += 1



def createPlaneImage(directory, outputDir, filename, 
                interactiveWindow=False):
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
    aRenderer.SetBackground(255/255, 255/255, 255/255)

    # Window size of final png file
    renWin.SetSize(750, 550)

    if interactiveWindow:
        x_locations = np.linspace(-2282674.723407029, 2304660.8051767494, 1)
    else:
        x_locations = np.linspace(-2282674.723407029, 2304660.8051767494, 300)
    scalar_value = "rho"
    opacity = 0.25


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

    dMax = np.amax(dary)
    dMin = np.amin(dary)

    
    # Coloring
    hueLut = vtk.vtkLookupTable()
    hueLut.SetTableRange(dMin, dMax)
    hueLut.SetHueRange(dMin, dMax)
    hueLut.SetRampToLinear()
    hueLut.SetSaturationRange(dMin, dMax)
    hueLut.SetValueRange(dMin, dMax)
    hueLut.SetTableValue(dMin, 0/255, 0/255, 255/255)
    hueLut.SetTableValue(dMax, 0/255, 0/255, 255/255)    
    hueLut.Build()

    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()

    ctf.AddRGBPoint(0.0, 0, 0, 0)
    ctf.AddRGBPoint(0.1, 55/255, 6/255, 23/255)
    ctf.AddRGBPoint(0.2, 106/255, 4/255, 15/255)
    ctf.AddRGBPoint(0.3, 157/255, 2/255, 8/255)
    ctf.AddRGBPoint(0.4, 208/255, 0, 0)
    ctf.AddRGBPoint(0.5, 220/255, 47/255, 2/255)
    ctf.AddRGBPoint(0.6, 232/255, 93/255, 4/255)
    ctf.AddRGBPoint(0.7, 244/255, 140/255, 6/255)
    ctf.AddRGBPoint(0.8, 250/255, 163/255, 7/255)
    ctf.AddRGBPoint(0.9, 255/255, 186/255, 8/255)
    ctf.AddRGBPoint(1, 255/255, 196/255, 9/255)

    hueLut = vtk.vtkLookupTable()
    hueLut.SetNumberOfTableValues(10)
    hueLut.Build()
    for i in range(0, 10):
        rgb = list(ctf.GetColor(float(i)/10))+[1]
        hueLut.SetTableValue(i, rgb)
    
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
    opacityTransferFunction.AddPoint(dMin+2*(dMax-dMin), opacity)
    volumeGradientOpacity = vtk.vtkPiecewiseFunction()
    volumeGradientOpacity.AddPoint(dMin, 0)
    volumeGradientOpacity.AddPoint(dMax, 0.1)

    # Create transfer mapping scalar value to color.
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.SetColorSpaceToDiverging()
    colorTransferFunction.SetHSVWrap(False)


    for x in x_locations:
        aRenderer = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(aRenderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renWin)
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        aRenderer.SetBackground(225/255, 225/255, 225/255)

        # Window size of final png file
        renWin.SetSize(750, 600)

        volumeGradientOpacity.AddPoint(dMax/2, opacity)
        colorTransferFunction.AddRGBPoint(dMin, 255/255, 255/255, 212/255) # light yellow
        colorTransferFunction.AddRGBPoint((dMax + dMin)/5, 254/255, 227/255, 145/255)
        colorTransferFunction.AddRGBPoint((dMax + dMin)/4, 254/255,196/255,79/255)
        colorTransferFunction.AddRGBPoint((dMax + dMin)/3, 254/255, 153/255, 41/255)
        colorTransferFunction.AddRGBPoint((dMax + dMin)/2, 217/255, 95/255, 14/255)
        colorTransferFunction.AddRGBPoint((dMax + dMin), 163/255,62/255,4/255)


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

        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        plane = vtk.vtkPlane()
        plane.SetOrigin(x, 900000.0000024999, -6.400048732757568e-01)
        plane.SetNormal(1, 0, 0)

        #create cutter
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputConnection(reader.GetOutputPort())
        cutter.Update()
        cutterMapper = vtk.vtkPolyDataMapper()
        cutterMapper.SetInputConnection(cutter.GetOutputPort())
        cutterMapper.SetLookupTable(hueLut)
        # cutterMapper.SetColorModeToDirectScalars()

        #create plane actor
        planeActor = vtk.vtkActor()
        planeActor.GetProperty().SetColor(0, 0, 1)
        planeActor.GetProperty().SetLineWidth(1)
        planeActor.SetMapper(cutterMapper)
        aRenderer.AddActor(planeActor)

        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        plane2 = vtk.vtkPlane()
        plane2.SetOrigin(0, 0, 0)
        plane2.SetNormal(0, 1, 0)

        #create cutter
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane2)
        cutter.SetInputConnection(reader.GetOutputPort())
        cutter.Update()
        cutterMapper = vtk.vtkPolyDataMapper()
        cutterMapper.SetInputConnection(cutter.GetOutputPort())
        cutterMapper.SetColorModeToDirectScalars()
        
        #create plane actor
        planeActor = vtk.vtkActor()
        planeActor.GetProperty().SetColor(1, 1, 1)
        planeActor.GetProperty().SetLineWidth(3)
        planeActor.SetMapper(cutterMapper)
        aRenderer.AddActor(planeActor)

        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 1, 0)
        aCamera.SetPosition(0, 0, 1) 
        aCamera.SetFocalPoint(0.6, 0.2, 0)
        aCamera.ComputeViewPlaneNormal()

        # Camera views
        aRenderer.SetActiveCamera(aCamera)
        aRenderer.ResetCamera()
        aRenderer.SetBackground(1, 1, 1)

        # Zooming in
        aCamera.Dolly(1.4)


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

            outputFile = outputDir+"/"+str(round(x)) + ".png"

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

    # scalars = ['rho', 'prs']
    # opacities = [0.8, 0.5]
    # createImage(stored_folder, prs_outputDir, "pv_insitu_300x300x300_22010.vti",
    #             scalars, opacities, interactiveWindow=True)
    # exit()
    # scalars = ['rho', 'prs']
    # opacities = [0.8, 0.5]
    # createImages(stored_folder, prs_outputDir, scalars,
    #              opacities, interactiveWindow=False)
    # exit()

    # createCSV(prs_outputDir, "cvlibd/server/data/volume-render/data_prs.csv", 
    #         num_yValues, num_xValues, output_type="prs")
    # exit()
    # createCSV(outputDir, "cvlibd/server/data/volume-render/data.csv", 
    #           num_yValues, num_xValues, output_type="scalars")
    # exit()

    # createGif(prs_outputDir, "GIFS/prs")
    # exit()

    # createGif_slices(outputDir, "GIFS/tev_slices")
    # exit()

    # Convert data to csv for plotting
    getInfo('data')
    exit()
    
    # Test image with one file
    # createPlaneImage('data', outputDir, "pv_insitu_300x300x300_22010.vti",
    #             interactiveWindow=True)
    # exit()


    # Choose scalar value to plot.
    # You can choose from 'v02', 'v03', 'prs' and 'tev'.
    print("Creating images")
    scalars = ['v02', 'v03', 'tev']
    opacities = [0.1, 0.3, 0.1]
    createImages(stored_folder, outputDir, scalars,
                 opacities, interactiveWindow=False)
    exit()

    # print("Creating pressure images")
    scalars = ['prs', 'rho']
    opacities = [0.7, 0.5]
    createImages(stored_folder, prs_outputDir, scalars,
                 opacities, interactiveWindow=False)
    exit()

    # Choose to comment function out or not
    createGif(outputDir, "GIFS/allscalars")
    createGif(prs_outputDir, "GIFS/prs")

    # Call this function in order to write the filenames to csv,
    # only used for the HTML-representation.
    createCSV(outputDir, "cvlibd/server/data/volume-render/data.csv", num_yValues,
              output_type="scalars")
    createCSV(prs_outputDir,
              "cvlibd/server/data/volume-render/data_prs.csv", num_yValues, output_type="prs")




