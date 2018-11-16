import cv2
import matplotlib.pyplot
from osgeo import gdal
import numpy
import sys, os
from gdalconst import *

from Helper import GeotiffHelper as GeotiffHelper
from Helper import FileHelper as fh
import Global as Global

#Configuration
TILE_PIXEL = 1000
TILE_SIZE_SPLIT = 500

def readImage(path):
    return cv2.imread(path)

def createPreview(filePath):
    GeotiffHelper.createPreview(filePath, Global.PREVIEW_PATH)

def createGridPreview(filePath):
    GeotiffHelper.createGridPreview(filePath, Global.GRID_PREVIEW_PATH, TILE_PIXEL)

def extractTile(tiffFile, xTile, yTile, tileSize):
    x = (xTile - 1 ) * tileSize
    y = (yTile - 1 ) * tileSize
    return GeotiffHelper.extractSubImage(tiffFile, Global.TILE_PATH, x, y, TILE_PIXEL, TILE_PIXEL)

def extractTiles(tiffFile, tileIds, tileSize):
    extractedTiles = []
    for id in tileIds:
        extractedTile = extractTile(tiffFile, id[0], id[1], tileSize)
        extractedTiles.append(extractedTile)
    return extractedTiles

def splitTile(tilePath, tileSize, splitTileSize):
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
            cv2.imwrite(Global.POST_PRE_DATASET_PATH + str(pixelRes[0]) + '_' +tempGps+".png",nextIm)


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
        extractTiles(Global.ORIGINAL_PATH+file, tileIds, TILE_PIXEL)

def createSplittedTile():
    for file in os.listdir(Global.TILE_PATH):
        splitTile(Global.TILE_PATH+file, TILE_PIXEL, TILE_SIZE_SPLIT)

def getTifInfo(tifPath):
    return GeotiffHelper.getTifInfo(tifPath)

def dev():
    print('dev...')
    data = fh.csvToDict(Global.DAMAGE_PREDICTION_PATH + 'buildings.csv')
    print('data[0]',data[0]['Id'] )
    print('len(data)',len(data))




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

init()
