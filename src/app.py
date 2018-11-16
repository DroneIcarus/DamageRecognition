import os, sys
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
    bp.detectBuilding('data/postPreDataSet/', 'data/buildingPredictions')

def dev():
    dp.dev()

actions = {
'preview' : preview,
'gridPreview' : gridPreview,
'tile': tile,
'splitTiles': splitTiles,
'test' : downloadTestImages,
'detectBuilding': detectBuilding,
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
