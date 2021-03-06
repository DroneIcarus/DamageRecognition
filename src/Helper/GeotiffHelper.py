import sys, os
import cv2
from osgeo import gdal
from gdalconst import *
import Global as Global
from Helper import FileHelper as fh
from Helper.BoundingBoxGPS import BoundingBoxGPS

def createPreview(imageToPreviewPath, resultDirectoryPath):
    im = cv2.imread(imageToPreviewPath, 3)
    out = cv2.resize(im,(1000,1000))
    im = None
    file = fh.extractFileNameAndExtension(imageToPreviewPath)
    cv2.imwrite(resultDirectoryPath+file,out)

def createGridPreview(imageToPreviewPath, resultDirectoryPath, tileSize):
    im = cv2.imread(imageToPreviewPath)
    imageName = fh.extractFileName(imageToPreviewPath)

    imgheight=im.shape[0]
    imgwidth=im.shape[1]
    #Number of tiles
    nbY = imgheight / tileSize
    nbX = imgwidth / tileSize

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
    cv2.imwrite(resultDirectoryPath + imageName + '.png',im)

def extractSubImageToArray(im, x, y, width, height, resultDirectoryPath=None):
    crop_img = im[y:y+height, x:x+width]
    if resultDirectoryPath:
        cv2.imwrite(resultDirectoryPath + '.png', crop_img)
    return crop_img

def extractSubImage(tiffPath, resultDirectoryPath, x, y, width, height):
    base = os.path.basename(tiffPath)
    tiffName = os.path.splitext(base)[0]
    tileFileName = resultDirectoryPath + tiffName + "_" + str(x)+"_"+str(y)+".tif"
    gdaltranString = "gdal_translate -of GTIFF -srcwin "+str(x)+", "+str(y)+", "+str(width)+", " \
        +str(height)+ " " + tiffPath + " " + tileFileName
    os.system(gdaltranString)
    return tileFileName

def pixelToGpsCoordinate(startCoordinate, pixelResolution, pixelPosition):
    delta = pixelResolution*pixelPosition
    if startCoordinate > 0:
        delta = delta * -1
    return startCoordinate + delta

def gpsCoordinateToPixel(startGpsCoordinate, resolution, pixelGpsCoordinate):
    delta = (startGpsCoordinate - pixelGpsCoordinate)
    if startGpsCoordinate < 0:
        delta = delta * -1
    return delta / resolution

#Input: BoundingBoxGPS  => Output: Array :[x1(lat1) y1(long1) x2(lat2) y2(long2)]
def gpsBoundingBoxToPixelArray(boundingBoxGPS, startLat, startLong, resolution):
    x1 = gpsCoordinateToPixel(startLat, resolution, boundingBoxGPS.lat1)
    y1 = gpsCoordinateToPixel(startLong, resolution, boundingBoxGPS.long1)
    x2 = gpsCoordinateToPixel(startLat, resolution, boundingBoxGPS.lat2)
    y2 = gpsCoordinateToPixel(startLong, resolution, boundingBoxGPS.long2)
    pixelBoundingBox = [int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))]
    return pixelBoundingBox

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

    # print('topLeftCoordinate', topLeftCoordinate)
    # print('bottomLeftCoordinate', bottomLeftCoordinate)
    # print('topRightCoordinate', topRightCoordinate)
    # print('bottomRightCoordinate', bottomRightCoordinate)

    rasterCount = dataset.RasterCount

    # print("Driver: {}/{}".format(dataset.GetDriver().ShortName,
    #                              dataset.GetDriver().LongName))
    # print("Size is {} x {} x {}".format(dataset.RasterXSize,
    #                                     dataset.RasterYSize,
    #                                     dataset.RasterCount))
    # print("Projection is {}".format(dataset.GetProjection()))
    #
    # print('geotransform',geotransform)
    # if geotransform:
    #     print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
    #     print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

    band = dataset.GetRasterBand(1)
    # print("Band Type={}".format(gdal.GetDataTypeName(band.DataType)))
    # if band.GetOverviewCount() > 0:
    #     print("Band has {} overviews".format(band.GetOverviewCount()))
    #
    # if band.GetRasterColorTable():
    #     print("Band has a color table with {} entries".format(band.GetRasterColorTable().GetCount()))

    return {
        'size': size,
        'pixelResolution': pixelResolution,
        'topLeftCoordinate': topLeftCoordinate,
        'bottomLeftCoordinate': bottomLeftCoordinate,
        'topRightCoordinate': topRightCoordinate,
        'bottomRightCoordinate': bottomRightCoordinate
        }

def resizeTiff(imageToResizePath, resizedImagePath, resizeFactor):
    im = cv2.imread(imageToResizePath)
    imgheight = im.shape[0] * resizeFactor
    imgwidth = im.shape[1] * resizeFactor
    gdaltranString = 'gdal_translate -of GTiff -outsize ' + str(imgwidth) + ' ' + str(imgheight) +' -r bilinear ' + imageToResizePath + ' ' + resizedImagePath
    os.system(gdaltranString)
