import os
import sys
import time
import datetime
import csv
import numpy as np

DIR_PROJECT = os.getcwd()
DIR_FILE = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(DIR_FILE)  # To find local version of the library
ROOT_DIR = DIR_FILE

# Download and install the Python COCO tools from https://github.com/waleedka/coco
# That's a fork from the original https://github.com/pdollar/coco with a bug
# fix for Python 3.
# I submitted a pull request https://github.com/cocodataset/cocoapi/pull/50
# If the PR is merged then use the original repo.
# Note: Edit PythonAPI/Makefile and replace "python" with "python3".
#
# A quick one liner to install the library
# !pip install git+https://github.com/waleedka/coco.git#subdirectory=PythonAPI
import skimage.io
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
from pycocotools import mask as maskUtils
import coco #a slightly modified version

from mrcnn.evaluate import build_coco_results, evaluate_coco
from mrcnn.dataset import MappingChallengeDataset
from mrcnn import visualize
import zipfile
import urllib.request
import shutil
import glob
import tqdm
import random
import cv2
import json

# Import Mask RCNN
from mrcnn.config import Config
from mrcnn import model as modellib, utils
from Helper import GeotiffHelper as gh
from Helper import FileHelper as fh
from Helper.BoundingBoxGPS import BoundingBoxGPS
from Helper.BuildingPrediction import BuildingPrediction
import Global as Global

PRETRAINED_MODEL_PATH = os.path.join(ROOT_DIR,"data/" "pretrained_weights.h5")
LOGS_DIRECTORY = os.path.join(ROOT_DIR, "logs")
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
IMAGE_DIR = os.path.join(ROOT_DIR, "data", "test", "images")

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 5
    NUM_CLASSES = 1 + 1  # 1 Background + 1 Building
    IMAGE_MAX_DIM=320
    IMAGE_MIN_DIM=320
    NAME = "crowdai-mapping-challenge"

def getBoundingBoxGPS(startLat, startLong, pixelResolution, pixelBoudingBox):
    lat1 = gh.pixelToGpsCoordinate(startLat, pixelResolution, pixelBoudingBox[0])
    long1 = gh.pixelToGpsCoordinate(startLong, pixelResolution, pixelBoudingBox[1])
    lat2 = gh.pixelToGpsCoordinate(startLat, pixelResolution, pixelBoudingBox[2])
    long2 = gh.pixelToGpsCoordinate(startLong, pixelResolution, pixelBoudingBox[3])
    return BoundingBoxGPS(lat1, long1, lat2, long2)

def predict(imageDirectory, resultDirectory):
    config = InferenceConfig()
    # config.display()

    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
    model_path = PRETRAINED_MODEL_PATH
    model.load_weights(model_path, by_name=True)

    class_names = ['BG', 'building'] # In our case, we have 1 class for the background, and 1 class for building

    file_names = next(os.walk(imageDirectory))[2]
    nbFiles = len(file_names)

    csvName = Global.PREDICTIONS_PATH + fh.getTimeStamp() + '.csv'
    #Create csv file to append the builing predictions
    fh.arrayToCsv(csvName, [['BuildingPrediction']])

    for fileIndex in range(0, nbFiles, config.BATCH_SIZE):
        images = []
        reste = nbFiles - (fileIndex+config.BATCH_SIZE)
        for i in range(0, config.BATCH_SIZE):
            if  config.BATCH_SIZE+reste > i:
                im = skimage.io.imread(os.path.join(imageDirectory, file_names[fileIndex+i]))
            images.append(im)

        predictions = model.detect(images, verbose=1) # We are replicating the same image to fill up the batch_size

        if reste < 0:
            del predictions[reste:]
        for j in range(0, len(predictions)):
            base = os.path.basename(file_names[fileIndex+j])
            imStringInfo = os.path.splitext(base)[0]
            imInfo = imStringInfo.split("_")
            resolution = float(imInfo[0])
            lat = float(imInfo[1])
            long = float(imInfo[2])
            predictionsToAdd = []
            resultPath = os.path.join(resultDirectory, file_names[fileIndex+j])
            p = predictions[j]
            imageResult = visualize.display_instances(images[j], p['rois'], p['masks'], p['class_ids'], class_names, p['scores'])
            for z in range(0,len(p['rois'])):
                boundingBox = getBoundingBoxGPS(lat, long, resolution, p['rois'][z])
                buildingPred = BuildingPrediction(str(fileIndex+j), boundingBox)
                predictionsToAdd.append([buildingPred.toJSON()])
                # pixelBox = gh.gpsBoundingBoxToPixelArray(boundingBox, lat, long, resolution)
                # predictionsToAdd.append([str(fileIndex+j), file_names[fileIndex+j], boundingBox.toJSON(), str(p['rois'][z]), pixelBox])
            imageResult.show()
            imageResult.savefig(resultPath)
        fh.arrayToCsv(csvName, predictionsToAdd)

def detectBuilding(directoryPath, resultDirectory):
    predict(directoryPath, resultDirectory)

def init():
    if not os.path.exists(Global.PREDICTIONS_PATH):
        print('Creating %s path'%(Global.PREDICTIONS_PATH))
        os.makedirs(Global.PREDICTIONS_PATH)

init()
