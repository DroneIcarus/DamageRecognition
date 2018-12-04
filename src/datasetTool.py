import os, sys
from PIL import Image
import Global as Global
from Helper import FileHelper as fh

def phil():
    print('Yo Phil!')
    with Image.open('im1.png') as img:
        img.show()
actions = {
'phil' : phil
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
