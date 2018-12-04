import csv
import sys
import requests
import skimage.io
import os
import glob
import pickle
import time

from IPython.display import display, Image, HTML
from keras.applications import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image as kimage
import numpy as np
import pandas as pd
import scipy.sparse as sp
import skimage.io

sys.path.append('../')
import helpers

def cosine_similarity(ratings):
    sim = ratings.dot(ratings.T)
    if not isinstance(sim, np.ndarray):
        sim = sim.toarray()
    norms = np.array([np.sqrt(np.diagonal(sim))])
    return (sim / norms / norms.T)

rand_img = 'im2.png'
Image(filename=rand_img)

img = kimage.load_img(rand_img, target_size=(224, 224))
x = kimage.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)
print(x.shape)
model = VGG16(include_top=False, weights='imagenet')
pred = model.predict(x)
print(pred.shape)
print(pred.ravel().shape)


df = pd.read_csv('model_likes_anon.psv',
                 sep='|', quoting=csv.QUOTE_MINIMAL,
                 quotechar='\\')
df.drop_duplicates(inplace=True)
df = helpers.threshold_interactions_df(df, 'uid', 'mid', 5, 5)
valid_mids = set(df.mid.unique())

get_mid = lambda x: x.split(os.path.sep)[-1].split('_')[0]
fnames = glob.glob('../data/model_thumbs/*_thumb200.jpg')
fnames = [f for f in fnames if get_mid(f) in valid_mids]
fnames = ['im2.png']

idx_to_mid = {}
batch_size = 500
min_idx = 0
max_idx = min_idx + batch_size
total_max = len(fnames)
n_dims = pred.ravel().shape[0]
px = 500

X = np.zeros(((max_idx - min_idx), px, px, 3))
img = kimage.load_img(fnames[0], target_size=(px, px))
img_array = kimage.img_to_array(img)
X[0 - min_idx, :, :, :] = img_array

print('Preprocess input')
t0 = time.time()
X = preprocess_input(X)
t1 = time.time()
print('{}'.format(t1 - t0))

print('Predicting')
t0 = time.time()
these_preds = model.predict(X)
shp = ((max_idx - min_idx) + 1, n_dims)

preds = preds.tocsr()
sim = cosine_similarity(preds)
    # Pl
