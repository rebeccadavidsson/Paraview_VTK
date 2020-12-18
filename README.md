# Paraview_VTK
Course in Scientific Visualization and Virtual Reality (UvA 2020)

Website:
https://rebeccadavidsson.github.io/Paraview_VTK/


![](GIFS/allscalars.gif)
![](GIFS/prs.gif)

## Data
Data is downloaded from http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/ and stored in the ```data``` folder.

## Dependencies
```pip3 install -r requirements.txt```

## Running scripts
Run the script to convert images from a given folder. Data has to be downloaded from the source given above in order to run the scripts.  Specify in which folder the data is stored. Default is ```data```. There are two main scripts to run. The first can be run with the command:

```
python3 VTKscript.py
```
and is used to create images, GIFS, and convert data to CSV. 
Another script that is used to read and write images to an external disk, can be run with 

```
python3 externalDisk.py
```
Other scripts are ```create_heatmap.py```, used for the heatmap GIFS (which can be seen under the section results of this README) and ```helpers.py```, which is used for both ```VTKscript.py``` and ```externalDisk.py```.

Furthermore, there is one notebook ```Plots.ipynb```, that is used to create plots with matplotlib, to show the water splash over time.

## Running the server (using cvlib)
The cvlib package was used for this project (https://github.com/arunponnusamy/cvlib), made by Arun Ponnusamy in 2018.

Run by:
```
python -m http.server 8080
```
and open the ```index.html```


### Results
Results can be found on the results page and the report ```report_SVVR_Sam_Rebecca.pdf```, found in this directory.

Temperature heatmaps of 4 different timesteps:
![](GIFS/temperature_13306.gif)
![](GIFS/temperature_22010.gif)
![](GIFS/temperature_35332.gif)
![](GIFS/temperature_49978.gif)


## Authors
* *Sam Verhezen*
* *Rebecca Davidsson*
