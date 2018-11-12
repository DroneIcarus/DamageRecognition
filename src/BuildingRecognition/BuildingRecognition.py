import os
from BuildingRecognitionM import startPred as BuildingPrediction

#Directories
DATA_PATH = 'data/'
PREDICTIONS_PATH = DATA_PATH + 'buildingPredictions/'

def detectBuilding(directoryPath, resultDirectory):
    BuildingPrediction.predict(directoryPath, resultDirectory)

def init():
    if not os.path.exists(PREDICTIONS_PATH):
        print('Creating %s path'%(PREDICTIONS_PATH))
        os.makedirs(PREDICTIONS_PATH)

init()
