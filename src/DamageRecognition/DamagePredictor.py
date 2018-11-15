import cv2
import matplotlib.pyplot
from osgeo import gdal
import numpy
import sys, os
from gdalconst import *

#Configuration
TILE_PIXEL = 1000
TILE_SIZE_SPLIT = 500

#Directories
DATA_PATH = 'data/'
ORIGINAL_PATH = DATA_PATH + 'original/'
PREVIEW_PATH = DATA_PATH + 'preview/'
GRID_PREVIEW_PATH = DATA_PATH + 'gridPreview/'
TILE_PATH = DATA_PATH + 'tiles/' #Image corresponding to a square in the gridPreview
POST_PRE_DATASET_PATH = DATA_PATH + 'postPreDataSet/'

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
    cv2.imwrite(PREVIEW_PATH+file,out)

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
    cv2.imwrite(GRID_PREVIEW_PATH + imageName + '.png',im)

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
            cv2.imwrite(POST_PRE_DATASET_PATH + str(pixelRes[0]) + '_' +tempGps+".png",nextIm)


#Call by app.py
def downloadTestImages():
    if not os.path.exists( ORIGINAL_PATH + '2130300_pre.tif'):
        getIm1 = 'curl -o ' + ORIGINAL_PATH + '2130300_pre.tif http://opendata.digitalglobe.com/hurricane-michael/pre-event/2018-07-28/1050010011549F00/2130300.tif'
        os.system(getIm1)
    if not os.path.exists( ORIGINAL_PATH + '2130300_post.tif'):
        getIm2 = 'curl -o ' + ORIGINAL_PATH + '2130300_post.tif http://opendata.digitalglobe.com/hurricane-michael/post-event/2018-10-13/105001001292DF00/2130300.tif'
        os.system(getIm2)

def getAllPreview():
    for file in os.listdir(ORIGINAL_PATH):
        createPreview(ORIGINAL_PATH+file)

def createAllGridPreview():
    for file in os.listdir(ORIGINAL_PATH):
        createGridPreview(ORIGINAL_PATH+file)

def createTiles(tileIds):
    for file in os.listdir(ORIGINAL_PATH):
        extractTiles(ORIGINAL_PATH+file, tileIds, TILE_PIXEL)

def createSplittedTile():
    for file in os.listdir(TILE_PATH):
        splitTiles(TILE_PATH+file, None, TILE_PIXEL, TILE_SIZE_SPLIT)

def getTifInfo(tifPath):
    dataset = gdal.Open(tifPath, gdal.GA_ReadOnly)
    geotransform = dataset.GetGeoTransform()

    xSize = dataset.RasterXSize
    ySize = dataset.RasterYSize
    size = [xSize, ySize]
    #w-e pixel resolution, n-s pixel resolution
    pixelResolution = [geotransform[1], geotransform[5]]

    #latitude, longitude
    topLeftCoordinate = [geotransform[3], geotransform[0]]
    bottomLeftCoordinate = [geotransform[3]+geotransform[5]*ySize, geotransform[0]]
    topRightCoordinate = [geotransform[3], geotransform[0]+geotransform[1]*xSize]
    bottomRightCoordinate = [geotransform[3]+geotransform[5]*ySize, geotransform[0]+geotransform[1]*xSize]

    print('topLeftCoordinate', topLeftCoordinate)
    print('bottomLeftCoordinate', bottomLeftCoordinate)
    print('topRightCoordinate', topRightCoordinate)
    print('bottomRightCoordinate', bottomRightCoordinate)

    rasterCount = dataset.RasterCount

    print("Driver: {}/{}".format(dataset.GetDriver().ShortName,
                                 dataset.GetDriver().LongName))
    print("Size is {} x {} x {}".format(dataset.RasterXSize,
                                        dataset.RasterYSize,
                                        dataset.RasterCount))
    print("Projection is {}".format(dataset.GetProjection()))

    print('geotransform',geotransform)
    if geotransform:
        print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
        print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

    band = dataset.GetRasterBand(1)
    print("Band Type={}".format(gdal.GetDataTypeName(band.DataType)))
    if band.GetOverviewCount() > 0:
        print("Band has {} overviews".format(band.GetOverviewCount()))

    if band.GetRasterColorTable():
        print("Band has a color table with {} entries".format(band.GetRasterColorTable().GetCount()))

    return {
        'size': size,
        'pixelResolution': pixelResolution,
        'topLeftCoordinate': topLeftCoordinate,
        'bottomLeftCoordinate': bottomLeftCoordinate,
        'topRightCoordinate': topRightCoordinate,
        'bottomRightCoordinate': bottomRightCoordinate
        }

def init():
    if not os.path.exists(DATA_PATH):
        print('Creating %s path'%(DATA_PATH))
        os.makedirs(DATA_PATH)
    if not os.path.exists(ORIGINAL_PATH):
        print('Creating %s path'%(ORIGINAL_PATH))
        os.makedirs(ORIGINAL_PATH)
    if not os.path.exists(PREVIEW_PATH):
        print('Creating %s path'%(PREVIEW_PATH))
        os.makedirs(PREVIEW_PATH)
    if not os.path.exists(GRID_PREVIEW_PATH):
        print('Creating %s path'%(GRID_PREVIEW_PATH))
        os.makedirs(GRID_PREVIEW_PATH)
    if not os.path.exists(TILE_PATH):
        print('Creating %s path'%(TILE_PATH))
        os.makedirs(TILE_PATH)
    if not os.path.exists(POST_PRE_DATASET_PATH):
        print('Creating %s path'%(POST_PRE_DATASET_PATH))
        os.makedirs(POST_PRE_DATASET_PATH)

init()
