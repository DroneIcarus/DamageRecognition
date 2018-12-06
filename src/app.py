import sys
import Global as Global
from DamageRecognition import DamagePredictor as dp
from Icarus import Icarus as icarus
from Helper import FileHelper as fh

# Create a preview image of each image in the ORIGINAL_PATH
def preview():
    dp.getAllPreview()

# Create a preview image of each image in the ORIGINAL_PATH and draw a grid on it
def gridPreview():
    dp.createAllGridPreview()

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

#Download 2 images from the hurricane-michael for testing
def downloadTestImages():
    dp.downloadTestImages()

def testIcarus():
    #1 Download test images
    dp.downloadTestImages()
    #2 To obtains test images
    # tiles = [[1,4],[1,5],[2,5],[3,5],[3,6],[4,6],[5,6],[5,7],[6,7],[6,6],[6,8],[7,8],[7,7],[8,7],[8,8],[8,9]]
    fh.deleteAllInDirectory(Global.TILE_PATH)
    fh.deleteAllInDirectory(Global.TEST_PRE_IMAGE_PATH)
    tiles = [[1, 4], [1, 5]]
    dp.createTiles(tiles)
    fh.moveAllFiles(Global.TILE_PATH, Global.TEST_PRE_IMAGE_PATH)

    #3 Check image in PreDisaster
    icarus.checkPreImage(Global.TEST_PRE_IMAGE_PATH)
    #4 Check image in PostDisaster
    icarus.checkPreImage(Global.TEST_POST_IMAGE_PATH)
    #5 Split pre image with the correct resolution to detect the buildings
    icarus.getBuildingSet(Global.TEST_PRE_IMAGE_PATH, Global.ICARUS_PRE_SPLIT_PATH)
    #6 Detect the building on pre images => Building prediction in csv
    icarus.detectBuilding(Global.ICARUS_PRE_SPLIT_PATH, Global.ICARUS_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    #7 Split post image with the correct resolution to detect the buildings
    icarus.getBuildingSet(Global.TEST_POST_IMAGE_PATH, Global.ICARUS_POST_SPLIT_PATH)
    #8 Detect the building on post images => Building prediction in csv
    icarus.detectBuilding(Global.ICARUS_POST_SPLIT_PATH, Global.ICARUS_POST_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    #9 Compare the result of the detected building
    icarus.compareBuilding(Global.ICARUS_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ICARUS_POST_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ICARUS_DAMAGE_RESULT_PATH)

def launchIcarus():
    #1 Check image in PreDisaster
    icarus.checkPreImage(Global.TEST_PRE_IMAGE_PATH)
    #2 Check image in PostDisaster
    icarus.checkPreImage(Global.TEST_POST_IMAGE_PATH)
    #3 Split pre image with the correct resolution to detect the buildings
    icarus.getBuildingSet(Global.TEST_PRE_IMAGE_PATH, Global.ICARUS_PRE_SPLIT_PATH)
    #4 Detect the building on pre images => Building prediction in csv
    icarus.detectBuilding(Global.ICARUS_PRE_SPLIT_PATH, Global.ICARUS_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    #5 Split post image with the correct resolution to detect the buildings
    icarus.getBuildingSet(Global.TEST_POST_IMAGE_PATH, Global.ICARUS_POST_SPLIT_PATH)
    #6 Detect the building on post images => Building prediction in csv
    icarus.detectBuilding(Global.ICARUS_POST_SPLIT_PATH, Global.ICARUS_POST_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    #7 Compare the result of the detected building
    icarus.compareBuilding(Global.ICARUS_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ICARUS_POST_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ICARUS_DAMAGE_RESULT_PATH)

actions = {
'preview' : preview,
'gridPreview' : gridPreview,
'tile': tile,
'downloadTestImages' : downloadTestImages,
'testIcarus': testIcarus,
'icarus': launchIcarus
}

if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg in actions:
        actions[arg]()
    else:
        print('Unknown parameters')
else:
    print('No parameter entered...')

