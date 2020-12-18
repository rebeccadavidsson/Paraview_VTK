
import numpy as np
import matplotlib.pylab as plt
import vtk
import vtk.util.numpy_support as VN
from PIL import Image


reader = vtk.vtkXMLImageDataReader()
reader.SetFileName('data/pv_insitu_300x300x300_22010.vti')
reader.Update()
dary = VN.vtk_to_numpy(
    reader.GetOutput().GetPointData().GetScalars('v02'))

f = dary.reshape(300, 300, 300)
f = np.swapaxes(f, 0, 1)
f = np.flipud(f)


def createGif(outputDir):
    """
    Returns a GIF from .png files in a given directory
    """
    print("Creating GIF")
    images = [i for i in range(0, 300)]
    images = [Image.open(outputDir + '/' + str(i) + ".png").convert('RGBA').quantize()
              for i in images]

    images[0].save('GIFS/tev_22010.gif',
                   optimize=False, 
                   duration=50,  
                   save_all=True,
                   loop=20,
                   append_images=images[1:])


def heatmap2d(arr: np.ndarray, i):
    # with plt.rc_context({'xtick.color': 'white', 'ytick.color': 'white', 'figure.facecolor': 'white'}):
    fig = plt.figure()
    plt.imshow(arr, cmap='gist_heat')  # gist_heat, plasma
    plt.colorbar()
    plt.axis('off')
    fig.savefig('heatmap/' + str(i), dpi=fig.dpi, transparent=False)
    plt.close()


def makeImages():
    for i in range(0, 300):
        test_array = f[:, :, i]
        heatmap2d(test_array, i)


makeImages()
createGif('heatmap')

