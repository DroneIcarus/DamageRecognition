import os
import sys
import time
import datetime
import csv

def getTimeStamp():
    now = datetime.datetime.now()
    return "%d-%d-%d-%d-%d"%(now.year, now.month, now.day, now.hour, now.minute)

    if not os.path.exists(Global.ORIGINAL_PATH + '2130300_pre.tif'):
        getIm1 = 'curl -o ' + Global.ORIGINAL_PATH + '2130300_pre.tif http://opendata.digitalglobe.com/hurricane-michael/pre-event/2018-07-28/1050010011549F00/2130300.tif'
        os.system(getIm1)

def isPathExist(path):
    return os.path.exists(path)

def arrayToCsv(fileName, data):
    writingOption = 'a'
    if not isPathExist(fileName):
        writingOption = 'w'
    with open(fileName, writingOption) as file:
        writer = csv.writer(file)
        writer.writerows(data)

def extractFileName(filePath):
    base = os.path.basename(filePath)
    return os.path.splitext(base)[0]

def extractFileNameAndExtension(filePath):
    return os.path.basename(filePath)
