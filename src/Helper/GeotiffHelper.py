import sys, os
from osgeo import gdal
from gdalconst import *
import Global as Global

def createPreview(filePath):
    im = cv2.imread(filePath, 3)
    out = cv2.resize(im,(1000,1000))
    im = None
    file = extractFileNameAndExtension(filePath)
    cv2.imwrite(Global.PREVIEW_PATH+file,out)

def pixelToGpsCoordinate(startCoordinate, pixelResolution, pixelPosition):
    delta = pixelResolution*pixelPosition
    if startCoordinate > 0:
        delta = delta * -1
    return startCoordinate + delta

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
