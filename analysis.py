
from numpy import unravel_index
import numpy as np
import pickle
import matplotlib.pylab as plt
import matplotlib
import vtk
import vtk.util.numpy_support as VN
from PIL import Image
import os


# reader = vtk.vtkXMLImageDataReader()
# reader.SetFileName('data/pv_insitu_300x300x300_22010.vti')
# reader.Update()
# dary = VN.vtk_to_numpy(
#     reader.GetOutput().GetPointData().GetScalars('v02'))

# pickle.dump(dary, open("save.p", "wb"))


f = pickle.load(open("save.p", "rb"))

f = f.reshape(300, 300, 300)
f = np.swapaxes(f, 0, 1)
f = np.flipud(f)


print(unravel_index(f.argmax(), f.shape)[1])

exit()

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

