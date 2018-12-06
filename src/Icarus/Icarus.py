import sys, os
import cv2
import json
from scipy import spatial
import numpy as np

from Helper import GeotiffHelper as gh
from Helper import FileHelper as fh
from BuildingRecognition import BuildingPredictor as bp
from DamageRecognition import DamagePredictor as dp
import Global as Global

BUILDING_RESOLUTION = float('1.495e-06') #meter per pixel
BUILDING_IMAGE_SIZE = 500 #pixel

#Valide si les images pre-désastres sont valides
def checkPreImage(prePath):
    isOk = True
    for file in os.listdir(prePath):
        fileExt = fh.extractFileExtension(file)
        if fileExt == '.tiff' or fileExt == '.tif':
            tifInfo = None
            try:
                tifInfo = gh.getTifInfo(prePath+file)
            except Exception as e:
                #Should log the exeception
                print('Cannot obtains GeoTransform from %s file'%(file))
                sys.exit()
        else:
            print('Image %s is not a tiff file'%(file))
            sys.exit()

#Subdivision des images contenus dans le dossier (prePath) à la bonne grosseur et résolution pour
#que la détection des bâtiments soit valide
def getBuildingSet(prePath, resultPath):
    fh.createDirectory(resultPath)
    fh.deleteAllInDirectory(resultPath)
    resizedTiffPath = 'resizeTiffTmp.tif'
    for file in os.listdir(prePath):
        tifInfo = gh.getTifInfo(prePath+file)
        pixelRes = tifInfo['pixelResolution']
        resizeFactor = pixelRes[0]/BUILDING_RESOLUTION
        gh.resizeTiff(prePath+file, resizedTiffPath, resizeFactor)
        tifInfo = gh.getTifInfo(resizedTiffPath)
        pixelRes = tifInfo['pixelResolution']
        topLeftGps = tifInfo['topLeftCoordinate']
        size = tifInfo['size']
        im = cv2.imread(resizedTiffPath)
        imgheight = im.shape[0]
        imgwidth = im.shape[1]

        print(size[0])
        print(imgheight)
        print(size[1])
        print(imgwidth)

        for y in range(0, imgheight, BUILDING_IMAGE_SIZE):
            for x in range(0, imgwidth, BUILDING_IMAGE_SIZE):
                nextIm = im[y:y+BUILDING_IMAGE_SIZE,x:x+BUILDING_IMAGE_SIZE]
                lat = topLeftGps[0] + pixelRes[1]*y
                long = topLeftGps[1] + pixelRes[0]*x
                tempGps = str(lat) + '_' + str(long)
                cv2.imwrite(resultPath + str(pixelRes[0]) + '_' +tempGps+".png",nextIm)

        y = imgheight - BUILDING_IMAGE_SIZE
        for x in range(0, imgwidth, BUILDING_IMAGE_SIZE):
            nextIm = im[y:y+BUILDING_IMAGE_SIZE,x:x+BUILDING_IMAGE_SIZE]
            lat = topLeftGps[0] + pixelRes[1]*y
            long = topLeftGps[1] + pixelRes[0]*x
            tempGps = str(lat) + '_' + str(long)
            cv2.imwrite(resultPath + str(pixelRes[0]) + '_' +tempGps+".png",nextIm)

        x = imgwidth - BUILDING_IMAGE_SIZE
        for y in range(0, imgheight, BUILDING_IMAGE_SIZE):
            nextIm = im[y:y+BUILDING_IMAGE_SIZE,x:x+BUILDING_IMAGE_SIZE]
            lat = topLeftGps[0] + pixelRes[1]*y
            long = topLeftGps[1] + pixelRes[0]*x
            tempGps = str(lat) + '_' + str(long)
            cv2.imwrite(resultPath + str(pixelRes[0]) + '_' +tempGps+".png",nextIm)

        y = imgheight - BUILDING_IMAGE_SIZE
        x = imgwidth - BUILDING_IMAGE_SIZE
        nextIm = im[y:imgheight,x:imgwidth]
        lat = topLeftGps[0] + pixelRes[1]*y
        long = topLeftGps[1] + pixelRes[0]*x
        tempGps = str(lat) + '_' + str(long)
        cv2.imwrite(resultPath + str(pixelRes[0]) + '_' +tempGps+".png",nextIm)

#Détection des bâtiments sur toutes les images contenues dans directoryPath et crée un fichier .csv avec les prédictions
def detectBuilding(directoryPath, resultDirectory, resultCsvName=None):
    fh.createDirectory(resultDirectory)
    bp.detectBuilding(directoryPath, resultDirectory, resultCsvName)

#Prend un fichier .csv de résultats de détection de bâtiements avant et un autre fichier de détection des bâtiments après
#désastres et compare les résultats pour y attributer un niveau de dégât
def compareBuilding(preBuildingResult, postBuildingResult, resultPath):
    fh.createDirectory(resultPath)
    prePredictions = fh.csvToDict(preBuildingResult)
    postPredictions = fh.csvToDict(postBuildingResult)

    centers = []
    nearests = []
    damagePredictions = []

    if len(prePredictions) > 0:
        for pred in prePredictions:
            damagePred = json.loads(pred['BuildingPrediction'])
            damagePred['DamageLevel'] = 3
            damagePredictions.append(damagePred)
            preBoundingBox = damagePred['BoundingBox']
            center = {
            'lat':(preBoundingBox['lat1']+preBoundingBox['lat2'])/2,
            'long':(preBoundingBox['long1']+preBoundingBox['long2'])/2
            }
            centers.append([center['lat'],center['long']])

    for pred in postPredictions:
        postBoundingBox = json.loads(pred['BuildingPrediction'])['BoundingBox']
        center = {
        'lat':(postBoundingBox['lat1']+postBoundingBox['lat2'])/2,
        'long':(postBoundingBox['long1']+postBoundingBox['long2'])/2
        }
        pt = [center['lat'],center['long']]
        distance,index = spatial.KDTree(centers).query(pt)
        nearest = damagePredictions[index]

        preBoundingBox = json.loads(prePredictions[index]['BuildingPrediction'])['BoundingBox']

        preWidth = abs(preBoundingBox['lat2'] - preBoundingBox['lat1'])
        preHeight = abs(preBoundingBox['long2'] - preBoundingBox['long1'])
        postWidth = abs(postBoundingBox['lat2'] - postBoundingBox['lat1'])
        postHeight = abs(postBoundingBox['long2'] - postBoundingBox['long1'])


        diffWidth = abs(((preWidth-postWidth)/preWidth)*100)
        diffHeight = abs(((preHeight-postHeight)/preHeight)*100)

        if diffWidth < 15 and diffHeight < 15:
            nearest['DamageLevel'] = 1
        elif diffWidth > 15 and diffWidth < 90:
            nearest['DamageLevel'] = 2
        elif diffHeight > 15 and diffHeight < 90:
            nearest['DamageLevel'] = 2
        # nearests.append([json.dumps(nearest)])

    for pred in damagePredictions:
        nearests.append([json.dumps(pred)])
    if os.path.exists(resultPath+'test.csv'):
        os.remove(resultPath+'test.csv')
    fh.arrayToCsv(resultPath+'test.csv', [['BuildingPrediction']])
    fh.arrayToCsv(resultPath+'test.csv', nearests)

    #TEST
    dp.drawBuildingOnTile(resultPath+'test.csv', Global.TEST_POST_IMAGE_PATH, resultPath)

def init():
    if not os.path.exists(Global.TEST_PRE_IMAGE_PATH):
        print('Creating %s path'%(Global.TEST_PRE_IMAGE_PATH))
        os.makedirs(Global.TEST_PRE_IMAGE_PATH)
    if not os.path.exists(Global.TEST_POST_IMAGE_PATH):
        print('Creating %s path'%(Global.TEST_POST_IMAGE_PATH))
        os.makedirs(Global.TEST_POST_IMAGE_PATH)

init()