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

def tileSimple():
    selectedTiles = [[1,4],[1,5],[2,4],[2,5],[3,5],[3,6],[4,6],[5,6],[5,7],[6,6],[6,7],[6,8],[7,6] \
                    ,[7,7],[7,8],[7,9],[8,6],[8,7],[8,8],[8,9],[9,6],[9,7],[9,8],[9,9],[9,10],[10,10] \
                    ,[10,11],[11,11],[11,12],[12,12],[12,13],[13,12],[13,13],[13,14],[14,14],[14,15],[15,14],[15,15],[15,16] \
                    ,[16,15],[16,16],[16,17],[17,16],[17,17]]
    dp.createTiles(selectedTiles)


def splitTiles():
    dp.createSplittedTile()

def downloadTestImages():
    dp.downloadTestImages()

def detectBuilding():
    bp.detectBuilding('data/postPreDataSet/', 'data/buildingPredictions')

actions = {
'preview' : preview,
'gridPreview' : gridPreview,
'tile': tile,
'tileSimple': tileSimple,
'splitTiles': splitTiles,
'test' : downloadTestImages,
'detectBuilding': detectBuilding
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
