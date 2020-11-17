import numpy as np
import pickle
import matplotlib.pylab as plt
import vtk
import vtk.util.numpy_support as VN
from PIL import Image
import os


# reader = vtk.vtkXMLImageDataReader()
# reader.SetFileName('data/pv_insitu_300x300x300_22010.vti')
# reader.Update()
# dary = VN.vtk_to_numpy(
#     reader.GetOutput().GetPointData().GetScalars('v03'))

# pickle.dump(dary, open("save.p", "wb"))


f = pickle.load(open("save.p", "rb"))

f = f.reshape(300, 300, 300)
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

    images[0].save('GIFS/v03_22010.gif',
                   optimize=False, 
                   duration=50,  
                   save_all=True,
                   append_images=images[1:])


def heatmap2d(arr: np.ndarray, i):
    fig = plt.figure()
    plt.imshow(arr, cmap='plasma') # gist_heat
    plt.colorbar()
    fig.savefig('heatmap/' + str(i), dpi=fig.dpi)
    plt.close()


def makeImages():
    for i in range(0, 300):
        test_array = f[:, :, i]
        heatmap2d(test_array, i)


makeImages()
createGif('heatmap')

