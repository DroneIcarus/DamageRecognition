# DamageRecognition

###Prerequistes

1. Linux OS
2. Docker must be installed (https://docs.docker.com)

### Installation

Run the command: sudo ./build.sh

### Test the installation

Run the command: sudo ./TestIcarus.sh

Images should be downloaded and damages should be recognized on it.
You should see the results in the folder 'src/data/icarus/'

###Utilisation

##### Run a damage recognition on a set of images

1. Put the pre-disaster satellite images in folder 'src/PreDisaster/'.
2. Put the post-disaster satellite or UAV images in folder 'src/PostDisaster/'.
3. Run the command: sudo ./LaunchIcarus.sh

##### To visualize the results

Open the html file 'DamageOnGoogleMap.html' and select the generated .csv file 
from LaunchIcarus.sh in the directory 'src/data/icarus/DamageResult/'. 

or

Check the images generated in the directory 'src/data/icarus/DamageResult/'.