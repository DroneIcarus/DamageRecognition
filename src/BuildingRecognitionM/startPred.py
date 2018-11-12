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

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 5
    NUM_CLASSES = 1 + 1  # 1 Background + 1 Building
    IMAGE_MAX_DIM=320
    IMAGE_MIN_DIM=320
    NAME = "crowdai-mapping-challenge"

# config = InferenceConfig()
# config.display()
#
# model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
# model_path = PRETRAINED_MODEL_PATH
# model.load_weights(model_path, by_name=True)
#
# class_names = ['BG', 'building'] # In our case, we have 1 class for the background, and 1 class for building
#
# file_names = next(os.walk(IMAGE_DIR))[2]
# random_image = skimage.io.imread(os.path.join(IMAGE_DIR, random.choice(file_names)))
#
# predictions = model.detect([random_image]*config.BATCH_SIZE, verbose=1) # We are replicating the same image to fill up the batch_size
# print('len',len(predictions))
#
# p = predictions[0]
# print('rois', p['rois'])
# print('class_ids', p['class_ids'])
# print('scores', p['scores'])
# visualize.display_instances(random_image, p['rois'], p['masks'], p['class_ids'],
#                             class_names, p['scores'])
# cv2.waitKey(0)
# cv2.destroyAllWindows()

#
# ################
# # Gather all JPG files in the test set as small batches
# files = glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))
# ALL_FILES=[]
# _buffer = []
# for _idx, _file in enumerate(files):
#     if len(_buffer) == config.IMAGES_PER_GPU * config.GPU_COUNT:
#         ALL_FILES.append(_buffer)
#         _buffer = []
#     else:
#         _buffer.append(_file)
#
# if len(_buffer) > 0:
#     ALL_FILES.append(_buffer)
#
# # Iterate over all the batches and predict
# _final_object = []
# for files in tqdm.tqdm(ALL_FILES):
#     images = [skimage.io.imread(x) for x in files]
#     predoctions = model.detect(images, verbose=0)
#     for _idx, r in enumerate(predoctions):
#         _file = files[_idx]
#         image_id = int(_file.split("/")[-1].replace(".jpg",""))
#         print(image_id)
#         for _idx, class_id in enumerate(r["class_ids"]):
#             if class_id == 1:
#                 mask = r["masks"].astype(np.uint8)[:, :, _idx]
#                 bbox = np.around(r["rois"][_idx], 1)
#                 bbox = [float(x) for x in bbox]
#                 _result = {}
#                 _result["image_id"] = image_id
#                 _result["category_id"] = 100
#                 _result["score"] = float(r["scores"][_idx])
#                 _mask = maskUtils.encode(np.asfortranarray(mask))
#                 _mask["counts"] = _mask["counts"].decode("UTF-8")
#                 _result["segmentation"] = _mask
#                 _result["bbox"] = [bbox[1], bbox[0], bbox[3] - bbox[1], bbox[2] - bbox[0]]
#                 _final_object.append(_result)

# fp = open("predictions.json", "w")
# import json
# print("Writing JSON...")
# fp.write(json.dumps(_final_object))
# fp.close()

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
