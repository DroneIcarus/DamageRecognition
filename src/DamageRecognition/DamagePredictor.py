import cv2
import matplotlib.pyplot
from osgeo import gdal
import numpy
import sys, os
from gdalconst import *

from Helper import GeotiffHelper as GeotiffHelper
import Global as Global

#Configuration
TILE_PIXEL = 1000
TILE_SIZE_SPLIT = 500

def readImage(path):
    return cv2.imread(path)

def extractFileName(filePath):
    base = os.path.basename(filePath)
    return os.path.splitext(base)[0]

def extractFileNameAndExtension(filePath):
    return os.path.basename(filePath)

def createPreview(filePath):
    im = cv2.imread(filePath, 3)
    out = cv2.resize(im,(1000,1000))
    im = None
    file = extractFileNameAndExtension(filePath)
    cv2.imwrite(Global.PREVIEW_PATH+file,out)

def createGridPreview(filePath):
    im = readImage(filePath)
    imageName = extractFileName(filePath)

    imgheight=im.shape[0]
    imgwidth=im.shape[1]
    #Number of tiles
    nbY = imgheight / TILE_PIXEL
    nbX = imgwidth / TILE_PIXEL

    #Resize
    im = cv2.resize(im,(int(imgheight//nbY),int(imgwidth//nbX)))
    imgheight=im.shape[0]
    imgwidth=im.shape[1]

    tileHeight = int(imgheight//nbY)
    tileWidth = int(imgwidth//nbX)
    y1 = 0
    x1 = 0
    #Draw a rectangle for each tile
    for y in range(0,imgheight,tileHeight):
        for x in range(0, imgwidth, tileWidth):
            y1 = y + tileHeight
            x1 = x + tileWidth
            tiles = im[y:y+tileHeight,x:x+tileWidth]
            cv2.rectangle(im, (x, y), (x1, y1), (0, 0, 255))
    cv2.imwrite(Global.GRID_PREVIEW_PATH + imageName + '.png',im)

def extractTile(tiffFile, xTile, yTile, tileSize):
    base = os.path.basename(tiffFile)
    tiffName = os.path.splitext(base)[0]
    i = (xTile - 1 ) * tileSize
    j = (yTile - 1 ) * tileSize
    tileFileName = TILE_PATH + tiffName + "_" + str(i)+"_"+str(j)+".tif"
    gdaltranString = "gdal_translate -of GTIFF -srcwin "+str(i)+", "+str(j)+", "+str(tileSize)+", " \
        +str(tileSize)+ " " + tiffFile + " " + tileFileName
    os.system(gdaltranString)
    return tileFileName

def extractTiles(tiffFile, tileIds, tileSize):
    extractedTiles = []
    for id in tileIds:
        extractedTile = extractTile(tiffFile, id[0], id[1], tileSize)
        extractedTiles.append(extractedTile)
    return extractedTiles

def splitTiles(tilePath, tileIds, tileSize, splitTileSize):
    #extractedTiles = extractTiles(tiffFilePath, tileIds, tileSize)
    #for tile in extractedTiles:
    #print('tile',tile)
    base = os.path.basename(tilePath)
    tiffName = os.path.splitext(base)[0]
    gdaltranString = 'gdal_translate -of GTiff -outsize 3000 3000 -r bilinear ' + tilePath + ' resample.tif'
    result = os.system(gdaltranString)
    tifInfo = getTifInfo('resample.tif')
    pixelRes = tifInfo['pixelResolution']
    topLeftGps = tifInfo['topLeftCoordinate']
    im =  readImage('resample.tif')

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
        splitTiles(Global.TILE_PATH+file, None, TILE_PIXEL, TILE_SIZE_SPLIT)

def getTifInfo(tifPath):
    return GeotiffHelper.getTifInfo(tifPath)

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
