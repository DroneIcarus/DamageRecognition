#!/bin/bash
fileid="1e4XeVCvRb_xKsHBBPphr4zqIFVnVt_Se"
filename="BuildingRecognition/data/pretrained_weights.h5"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie