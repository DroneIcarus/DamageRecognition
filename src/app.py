import os, sys
import Global as Global
from DamageRecognition import DamagePredictor as dp
from BuildingRecognition import BuildingPredictor as bp
from Icarus import Icarus as icarus
from Helper import FileHelper as fh

def preview():
    dp.getAllPreview()

def gridPreview():
    dp.createAllGridPreview()

# No parameter : Extract all the tile from the imageName
# With array of tile position: Extract the selected tile (Example: python app.py tile 1:2,2:10  => Extract the tile 1-2 et 2-10)
def tile():
    selectedTiles = []
    if len(sys.argv) > 2:
        arg2 = sys.argv[2].replace('[', '')
        arg2 = arg2.replace(']', '')
        stringTiles = arg2.split(',')
        for tile in stringTiles:
            position = tile.split(':')
            selectedTiles.append([int(position[0]),int(position[1])])
        dp.createTiles(selectedTiles)
    else:
        print('Extracting all tiles are not implemented...')

def splitTiles():
    dp.createSplittedTile()

def downloadTestImages():
    dp.downloadTestImages()

def detectBuilding():
    bp.detectBuilding(Global.POST_PRE_DATASET_PATH, Global.PREDICTIONS_PATH)

def buildDataset():
    print('############################################')
    print('Downloading the post and pre disaster satellite image')
    print('############################################')
    # dp.downloadTestImages()
    print('############################################')
    print('Get some tiles from the pre disaster image')
    print('############################################')
    # dp.createDataSetTiles()
    print('############################################')
    print('Splitting tiles into small image for the building recogniton')
    print('############################################')
    # dp.createDatasetSplittedTile()
    print('############################################')
    print('Detecting building from the images extracted from the tiles')
    print('############################################')
    # bp.detectBuilding(Global.PRE_BUILDING_PATH, Global.PRE_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    print('############################################')
    print('Draw building on the tile images')
    print('############################################')
    dp.drawBuildingOnTile(Global.PRE_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.TILE_PREDISASTER_PATH, Global.PRE_BUILDING_RESULT_PATH)
    print('############################################')
    print('Get image of same size with detected building on the center')
    print('############################################')
    # dp.extractBuildingImage(Global.PRE_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ORIGINAL_PATH+'2130300_pre.tif', Global.ORIGINAL_PATH+'2130300_post.tif', Global.TRAIN_DATASET_PATH)
    print('############################################')
    print('DEV')
    print('############################################')
    #dp.dev(Global.DATASET_PATH+'labels.csv', Global.TILE_PREDISASTER_PATH, Global.DATASET_PATH)

def dev():
    dp.dev(Global.DATASET_PATH+'labels.csv', Global.TILE_PREDISASTER_PATH, Global.DATASET_PATH+'result/')

def testIcarus():
    #1 Download test images
    dp.downloadTestImages()
    #2 To obtains test images
    # tiles = [[1,4],[1,5],[2,5],[3,5],[3,6],[4,6],[5,6],[5,7],[6,7],[6,6],[6,8],[7,8],[7,7],[8,7],[8,8],[8,9]]
    fh.deleteAllInDirectory(Global.TILE_PATH)
    fh.deleteAllInDirectory(Global.TEST_PRE_IMAGE_PATH)

    dp.createTiles([[1,4],[1,5],[2,5],[3,5],[3,6],[4,6],[5,6],[5,7],[6,7],[6,6],[6,8],[7,8],[7,7],[8,7],[8,8],[8,9]])
    fh.moveAllFiles(Global.TILE_PATH, Global.TEST_PRE_IMAGE_PATH)

    # #3 Check image in PreDisaster
    # icarus.checkPreImage(Global.TEST_PRE_IMAGE_PATH)
    # #4 Check image in PostDisaster
    # icarus.checkPreImage(Global.TEST_POST_IMAGE_PATH)
    # #5 Split pre image with the correct resolution to detect the buildings
    # icarus.getBuildingSet(Global.TEST_PRE_IMAGE_PATH, Global.ICARUS_PRE_SPLIT_PATH)
    # # #6 Detect the building => Building prediction in csv
    # icarus.detectBuilding(Global.ICARUS_PRE_SPLIT_PATH, Global.ICARUS_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    # #
    # # icarus.getBuildingSet(Global.TEST_POST_IMAGE_PATH, Global.ICARUS_POST_SPLIT_PATH)
    # # icarus.detectBuilding(Global.ICARUS_POST_SPLIT_PATH, Global.ICARUS_POST_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    # icarus.compareBuilding(Global.ICARUS_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ICARUS_POST_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ICARUS_DAMAGE_RESULT_PATH)
    #


def launchIcarus(prePath, postPath):
    print('ica')
    #1 -Check image in PreDisaster
    # To obtains tests images dp.createTiles([[1,5],[2,5]])
    #tiki [[1,5],[2,5],[3,5],[3,6],[4,6],[5,6],[6,6],[6,7],[7,7],[8,7],[8,8],[8,9],[9,7],[11,12],[12,13]]
    #brian [[3,5],[3,6],[4,6]]
    #joel [[5,6],[6,6],[6,7],[7,7]]
    #phil [[8,7],[8,8],[9,7]]
    #jocelyne [[8,9]]
    #mike [[11,12]]
    #jason [[12,13]]

    #2 -Split image with the correct resolution to detect the buildings
    #3 -Detect the building => Building prediction in csv
    #4 -Check image in PostDisaster
    #5 -Obtains Post-Disaster images depending of the building predictions with the correct resolution to detect the damage
    #6 -Detect the damage => DamagePrediction in csv


actions = {
'preview' : preview,
'gridPreview' : gridPreview,
'tile': tile,
'splitTiles': splitTiles,
'test' : downloadTestImages,
'detectBuilding': detectBuilding,
'buildDataset' : buildDataset,
'testIcarus': testIcarus,
'icarus': launchIcarus,
'dev': dev
}

if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg in actions:
        actions[arg]()
    else:
        print('Unknown parameters')
else:
    print('No parameter entered...')

#dp.getAllPreview()
