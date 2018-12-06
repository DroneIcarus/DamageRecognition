import cv2
import matplotlib.pyplot
from osgeo import gdal
import numpy as np
import sys, os
import json
from gdalconst import *

from Helper import GeotiffHelper as GeotiffHelper
from Helper import FileHelper as fh
import Global as Global
#Class
from Helper.BuildingPrediction import BuildingPrediction
from Helper.BoundingBoxGPS import BoundingBoxGPS

#Configuration
TILE_PIXEL = 1000
TILE_SIZE_SPLIT = 500

def readImage(path):
    return cv2.imread(path)

def createPreview(filePath):
    GeotiffHelper.createPreview(filePath, Global.PREVIEW_PATH)

def createGridPreview(filePath):
    GeotiffHelper.createGridPreview(filePath, Global.GRID_PREVIEW_PATH, TILE_PIXEL)

def extractTile(tiffFile, xTile, yTile, tileSize, destinationPath):
    x = (xTile - 1 ) * tileSize
    y = (yTile - 1 ) * tileSize
    return GeotiffHelper.extractSubImage(tiffFile, destinationPath, x, y, TILE_PIXEL, TILE_PIXEL)

def extractTiles(tiffFile, tileIds, tileSize, destinationPath):
    extractedTiles = []
    for id in tileIds:
        extractedTile = extractTile(tiffFile, id[0], id[1], tileSize, destinationPath)
        extractedTiles.append(extractedTile)
    return extractedTiles

def splitTile(tilePath, tileSize, splitTileSize, destinationPath):
    resizedTiffPath = 'resizeTiffTmp.tif'
    GeotiffHelper.resizeTiff(tilePath, resizedTiffPath, 3)
    tifInfo = getTifInfo(resizedTiffPath)
    pixelRes = tifInfo['pixelResolution']
    topLeftGps = tifInfo['topLeftCoordinate']
    im =  readImage(resizedTiffPath)
    imgheight=im.shape[0]
    imgwidth=im.shape[1]
    x = 0
    y = 0
    for y in range(0, imgheight, splitTileSize):
        for x in range(0, imgwidth, splitTileSize):
            nextIm = im[y:y+splitTileSize,x:x+splitTileSize]
            lat = topLeftGps[0] + pixelRes[1]*y
            long = topLeftGps[1] + pixelRes[0]*x
            tempGps = str(lat) + '_' + str(long)
            cv2.imwrite(destinationPath + str(pixelRes[0]) + '_' +tempGps+".png",nextIm)


#Call by app.py
def downloadTestImages():
    if not os.path.exists(Global.ORIGINAL_PATH + '2130300_pre.tif'):
        getIm1 = 'curl -o ' + Global.ORIGINAL_PATH + '2130300_pre.tif http://opendata.digitalglobe.com/hurricane-michael/pre-event/2018-07-28/1050010011549F00/2130300.tif'
        os.system(getIm1)
    if not os.path.exists(Global.ORIGINAL_PATH + '2130300_post.tif'):
        getIm2 = 'curl -o ' +Global.ORIGINAL_PATH + '2130300_post.tif http://opendata.digitalglobe.com/hurricane-michael/post-event/2018-10-13/105001001292DF00/2130300.tif'
        os.system(getIm2)

def getAllPreview():
    for file in os.listdir(Global.ORIGINAL_PATH):
        createPreview(Global.ORIGINAL_PATH+file)

def createAllGridPreview():
    for file in os.listdir(Global.ORIGINAL_PATH):
        createGridPreview(Global.ORIGINAL_PATH+file)

def createTiles(tileIds):
    for file in os.listdir(Global.ORIGINAL_PATH):
        extractTiles(Global.ORIGINAL_PATH+file, tileIds, TILE_PIXEL, Global.TILE_PATH)

def createSplittedTile():
    for file in os.listdir(Global.TILE_PATH):
        splitTile(Global.TILE_PATH+file, TILE_PIXEL, TILE_SIZE_SPLIT, Global.POST_PRE_DATASET_PATH)

def getTifInfo(tifPath):
    return GeotiffHelper.getTifInfo(tifPath)

#Dataset
def createDataSetTiles():
    # tileIds = [[1,5],[2,5]]
    #tiki [[1,5],[2,5]]
    #brian [[3,5],[3,6],[4,6]]
    #joel [[5,6],[6,6],[6,7],[7,7]]
    #phil [[8,7],[8,8],[9,7]]
    #jocelyne [[8,9]]
    #mike [[11,12]]
    #jason [[12,13]]
    tileIds = [[12,13]]
    extractTiles(Global.ORIGINAL_PATH+'2130300_pre.tif', tileIds, TILE_PIXEL, Global.TILE_PREDISASTER_PATH)

def createDatasetSplittedTile():
    for file in os.listdir(Global.TILE_PREDISASTER_PATH):
        splitTile(Global.TILE_PREDISASTER_PATH+file, TILE_PIXEL, TILE_SIZE_SPLIT, Global.PRE_BUILDING_PATH)

def drawBuildingOnTile(csvBuildingPath, tilesPath, imageResultPath):
        # data = fh.csvToDict(Global.PRE_BUILDING_RESULT_PATH + Global.BUILDING_CSV_NAME + '.csv')
        data = fh.csvToDict(csvBuildingPath)
        for file in os.listdir(tilesPath):
            tifInfo = getTifInfo(tilesPath+file)
            pixelRes = tifInfo['pixelResolution']
            topLeftGps = tifInfo['topLeftCoordinate']
            im =  readImage(tilesPath+file)
            for line in data:
                if 'BuildingPrediction' in line:
                    damPred = json.loads(line['BuildingPrediction'])
                    bBox = BoundingBoxGPS(damPred['BoundingBox']['lat1'], damPred['BoundingBox']['long1'], damPred['BoundingBox']['lat2'], damPred['BoundingBox']['long2'])
                    buildPred = BuildingPrediction(damPred['Id'], bBox)
                    pt1 = GeotiffHelper.gpsBoundingBoxToPixelArray(bBox, topLeftGps[0], topLeftGps[1], pixelRes[0])
                    rectColor = (255,0,0)
                    if 'DamageLevel' in damPred:
                        damageLevel = int(damPred['DamageLevel'])
                        if damageLevel == 1:
                            rectColor = (0,255,0)
                        if damageLevel == 2:
                            rectColor = (0,255,255)
                        if damageLevel == 3:
                            rectColor = (0,0,255)
                    cv2.rectangle(im, (pt1[1], pt1[0]), (pt1[3], pt1[2]), rectColor)
            cv2.imwrite(imageResultPath+fh.extractFileName(file)+'.png',im)

def extractBuildingImage(csvBuildingPath, preDisasterPath, postDisasterPath, imageResultPath):
    data = fh.csvToDict(csvBuildingPath)

    preTifInfo = getTifInfo(preDisasterPath)
    postTifInfo = getTifInfo(postDisasterPath)

    preResolution = preTifInfo['pixelResolution'][0]
    postResolution = postTifInfo['pixelResolution'][0]
    preTopLeft = preTifInfo['topLeftCoordinate']
    postTopLeft = postTifInfo['topLeftCoordinate']

    preIm = readImage(preDisasterPath)
    postIm = readImage(postDisasterPath)
    predictionsToAdd = []
    for line in data:
        if 'BuildingPrediction' in line:
            damPred = json.loads(line['BuildingPrediction'])
            id = damPred['Id']
            bBox = BoundingBoxGPS(damPred['BoundingBox']['lat1'], damPred['BoundingBox']['long1'], damPred['BoundingBox']['lat2'], damPred['BoundingBox']['long2'])
            buildPred = BuildingPrediction(damPred['Id'], bBox)

            prePt = GeotiffHelper.gpsBoundingBoxToPixelArray(bBox, preTopLeft[0], preTopLeft[1], preResolution)
            buildingWidth = prePt[2] - prePt[0]
            buildingHeight = prePt[3] - prePt[1]

            x = max(0, prePt[1] - 25)
            y = max(0, prePt[0] - 25)
            # GeotiffHelper.extractSubImage(preDisasterPath, imageResultPath, x, y, buildingWidth+50, buildingHeight+50)
            building_img = GeotiffHelper.extractSubImageToArray(preIm, x, y, buildingWidth+50, buildingHeight+50)
            building_img2 = GeotiffHelper.extractSubImageToArray(postIm, x, y, buildingWidth+50, buildingHeight+50)

            preName = str(id)+'_A'+ '.png'
            postName = str(id)+'_B'+ '.png'
            predictionsToAdd.append([buildPred.toJSON(), preName])
            predictionsToAdd.append([buildPred.toJSON(), postName])
            # imageResult.show()
            # imageResult.savefig(resultPath)

            fh.arrayToCsv(Global.TRAIN_DATASET_PATH+'label.csv', predictionsToAdd)

            blackImg = np.zeros((300,300,3), np.uint8)
            blackImg2 = np.zeros((300,300,3), np.uint8)
            blackImg[0:buildingHeight+50, 0:buildingWidth+50] = building_img
            blackImg2[0:buildingHeight+50, 0:buildingWidth+50] = building_img2

            # cv2.imwrite(imageResultPath+str(id)+'_A' + '.png', blackImg)
            # cv2.imwrite(imageResultPath+str(id)+'_B' + '.png', blackImg2)

            cv2.imwrite(Global.TRAIN_DATASET_PRE_PATH+str(id)+'_A' + '.png', blackImg)
            cv2.imwrite(Global.TRAIN_DATASET_PRE_PATH+str(id)+'_B' + '.png', blackImg)

            cv2.imwrite(Global.TRAIN_DATASET_POST_PATH+str(id)+'_A' + '.png', blackImg)
            cv2.imwrite(Global.TRAIN_DATASET_POST_PATH+str(id)+'_B' + '.png', blackImg2)

            # compIm = np.zeros((buildingHeight+50,2*(buildingWidth+60),3), np.uint8)
            # compIm[0:buildingHeight+50, 0:buildingWidth+50] = building_img
            # compIm[0:buildingHeight+50, buildingWidth+50:2*(buildingWidth+50)] = building_img2
            # cv2.imwrite(Global.LABELING_DATSET_PATH+str(id)+'_B' + '.png', compIm)


            # GeotiffHelper.extractSubImageToArray(preIm, x, y, buildingWidth+50, buildingHeight+50, resultDirectoryPath=imageResultPath+str(x)+'_'+str(y))

def dev(csvPath, tilesPath, imageResultPath):
    red = (0, 0, 255)
    green = (0, 255, 0)
    yellow = (0, 255, 255)
    blue = (255, 0 ,0)
    data = fh.csvToDict(csvPath)
    for file in os.listdir(tilesPath):
        tifInfo = getTifInfo(tilesPath+file)
        pixelRes = tifInfo['pixelResolution']
        topLeftGps = tifInfo['topLeftCoordinate']
        im =  readImage(tilesPath+file)
        for line in data:
            color = blue
            if 'BuildingPrediction' in line and 'Label' in line:
                damPred = json.loads(line['BuildingPrediction'])
                label = int(line['Label'])
                if label == 1:
                    color = green
                if label == 2:
                    color = yellow
                if label == 3:
                    color = red
                bBox = BoundingBoxGPS(damPred['BoundingBox']['lat1'], damPred['BoundingBox']['long1'], damPred['BoundingBox']['lat2'], damPred['BoundingBox']['long2'])
                buildPred = BuildingPrediction(damPred['Id'], bBox)
                pt1 = GeotiffHelper.gpsBoundingBoxToPixelArray(bBox, topLeftGps[0], topLeftGps[1], pixelRes[0])
                cv2.rectangle(im, (pt1[1], pt1[0]), (pt1[3], pt1[2]), color)
        cv2.imwrite(imageResultPath+fh.extractFileName(file)+'.png',im)


def init():
    if not os.path.exists(Global.DATA_PATH):
        print('Creating %s path'%(Global.DATA_PATH))
        os.makedirs(Global.DATA_PATH)
    if not os.path.exists(Global.ORIGINAL_PATH):
        print('Creating %s path'%(Global.ORIGINAL_PATH))
        os.makedirs(Global.ORIGINAL_PATH)
    if not os.path.exists(Global.PREVIEW_PATH):
        print('Creating %s path'%(Global.PREVIEW_PATH))
        os.makedirs(Global.PREVIEW_PATH)
    if not os.path.exists(Global.GRID_PREVIEW_PATH):
        print('Creating %s path'%(Global.GRID_PREVIEW_PATH))
        os.makedirs(Global.GRID_PREVIEW_PATH)
    if not os.path.exists(Global.TILE_PATH):
        print('Creating %s path'%(Global.TILE_PATH))
        os.makedirs(Global.TILE_PATH)
    if not os.path.exists(Global.POST_PRE_DATASET_PATH):
        print('Creating %s path'%(Global.POST_PRE_DATASET_PATH))
        os.makedirs(Global.POST_PRE_DATASET_PATH)

    if not os.path.exists(Global.DATASET_PATH):
        print('Creating %s path'%(Global.DATASET_PATH))
        os.makedirs(Global.DATASET_PATH)
    if not os.path.exists(Global.TILE_PREDISASTER_PATH):
        print('Creating %s path'%(Global.TILE_PREDISASTER_PATH))
        os.makedirs(Global.TILE_PREDISASTER_PATH)
    if not os.path.exists(Global.PRE_BUILDING_PATH):
        print('Creating %s path'%(Global.PRE_BUILDING_PATH))
        os.makedirs(Global.PRE_BUILDING_PATH)
    if not os.path.exists(Global.PRE_BUILDING_RESULT_PATH):
        print('Creating %s path'%(Global.PRE_BUILDING_RESULT_PATH))
        os.makedirs(Global.PRE_BUILDING_RESULT_PATH)
    if not os.path.exists(Global.TRAIN_DATASET_PATH):
        print('Creating %s path'%(Global.TRAIN_DATASET_PATH))
        os.makedirs(Global.TRAIN_DATASET_PATH)
    if not os.path.exists(Global.LABELING_DATSET_PATH):
        print('Creating %s path'%(Global.LABELING_DATSET_PATH))
        os.makedirs(Global.LABELING_DATSET_PATH)
    if not os.path.exists(Global.TRAIN_DATASET_PRE_PATH):
        print('Creating %s path'%(Global.TRAIN_DATASET_PRE_PATH))
        os.makedirs(Global.TRAIN_DATASET_PRE_PATH)
    if not os.path.exists(Global.TRAIN_DATASET_POST_PATH):
        print('Creating %s path'%(Global.TRAIN_DATASET_POST_PATH))
        os.makedirs(Global.TRAIN_DATASET_POST_PATH)

init()
