import os, sys
import Global as Global
from DamageRecognition import DamagePredictor as dp
from BuildingRecognition import BuildingPredictor as bp

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
    dp.downloadTestImages()
    print('############################################')
    print('Get some tiles from the pre disaster image')
    print('############################################')
    dp.createDataSetTiles()
    print('############################################')
    print('Splitting tiles into small image for the building recogniton')
    print('############################################')
    dp.createDatasetSplittedTile()
    print('############################################')
    print('Detecting building from the images extracted from the tiles')
    print('############################################')
    bp.detectBuilding(Global.PRE_BUILDING_PATH, Global.PRE_BUILDING_RESULT_PATH, resultCsvName=Global.BUILDING_CSV_NAME)
    print('############################################')
    print('Draw building on the tile images')
    print('############################################')
    dp.drawBuildingOnTile(Global.PRE_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.TILE_PREDISASTER_PATH, Global.PRE_BUILDING_RESULT_PATH)
    print('############################################')
    print('Get image of same size with detected building on the center')
    print('############################################')
    dp.extractBuildingImage(Global.PRE_BUILDING_RESULT_PATH+Global.BUILDING_CSV_NAME+'.csv', Global.ORIGINAL_PATH+'2130300_pre.tif', Global.ORIGINAL_PATH+'2130300_post.tif', Global.TRAIN_DATASET_PATH)


def dev():
    dp.dev()

actions = {
'preview' : preview,
'gridPreview' : gridPreview,
'tile': tile,
'splitTiles': splitTiles,
'test' : downloadTestImages,
'detectBuilding': detectBuilding,
'buildDataset' : buildDataset,
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
