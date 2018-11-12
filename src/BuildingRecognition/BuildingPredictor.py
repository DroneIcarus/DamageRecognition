import os
import sys
import time
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

# Import Mask RCNN
from mrcnn.config import Config
from mrcnn import model as modellib, utils

PRETRAINED_MODEL_PATH = os.path.join(ROOT_DIR,"data/" "pretrained_weights.h5")
LOGS_DIRECTORY = os.path.join(ROOT_DIR, "logs")
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
IMAGE_DIR = os.path.join(ROOT_DIR, "data", "test", "images")

#Directories
DATA_PATH = 'data/'
PREDICTIONS_PATH = DATA_PATH + 'buildingPredictions/'

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 5
    NUM_CLASSES = 1 + 1  # 1 Background + 1 Building
    IMAGE_MAX_DIM=320
    IMAGE_MIN_DIM=320
    NAME = "crowdai-mapping-challenge"

def predict(imageDirectory, resultDirectory):
    config = InferenceConfig()
    # config.display()

    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
    model_path = PRETRAINED_MODEL_PATH
    model.load_weights(model_path, by_name=True)

    class_names = ['BG', 'building'] # In our case, we have 1 class for the background, and 1 class for building

    file_names = next(os.walk(imageDirectory))[2]
    nbFiles = len(file_names)
    for fileIndex in range(0, nbFiles, config.BATCH_SIZE):
        images = []
        reste = nbFiles - (fileIndex+config.BATCH_SIZE)
        for i in range(0, config.BATCH_SIZE):
            if  config.BATCH_SIZE+reste > i:
                print('i',i)
                im = skimage.io.imread(os.path.join(imageDirectory, file_names[fileIndex+i]))
            images.append(im)

        predictions = model.detect(images, verbose=1) # We are replicating the same image to fill up the batch_size
        if reste < 0:
            del predictions[reste:]
        for j in range(0, len(predictions)):
            resultPath = os.path.join(resultDirectory, file_names[fileIndex+j])
            p = predictions[j]
            imageResult = visualize.display_instances(images[j], p['rois'], p['masks'], p['class_ids'],
                                        class_names, p['scores'])
            imageResult.show()
            imageResult.savefig(resultPath)

    # for fileName in file_names:
    #     # fileName = random.choice(file_names)
    #     random_image = skimage.io.imread(os.path.join(imageDirectory, fileName))
    #     resultPath = os.path.join(resultDirectory, fileName)
    #
    #     predictions = model.detect([random_image]*config.BATCH_SIZE, verbose=1) # We are replicating the same image to fill up the batch_size
    #     print('len',len(predictions))
    #
    #     p = predictions[0]
    #     print('rois', p['rois'])
    #     print('class_ids', p['class_ids'])
    #     print('scores', p['scores'])
    #     p = predictions[1]
    #     print('rois', p['rois'])
    #     print('class_ids', p['class_ids'])
    #     print('scores', p['scores'])
    #     imageResult = visualize.display_instances(random_image, p['rois'], p['masks'], p['class_ids'],
    #                                 class_names, p['scores'])
    #     imageResult.show()
    #     imageResult.savefig(resultPath)
def detectBuilding(directoryPath, resultDirectory):
    predict(directoryPath, resultDirectory)

def init():
    if not os.path.exists(PREDICTIONS_PATH):
        print('Creating %s path'%(PREDICTIONS_PATH))
        os.makedirs(PREDICTIONS_PATH)

init()
