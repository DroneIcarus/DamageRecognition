#!/bin/bash
imageName=icarus_image
containerName=icarus

docker rmi $imageName
docker build -t $imageName .

#acces the bash container: sudo docker attach $containerName
#update code container: sudo docker cp devApp/. $containerName:/app/
#kill all containers: sudo docker kill $(sudo docker ps -q)
#remove all containers: sudo docker rm $(sudo docker ps -a -q)
#remove all images: sudo docker rmi $(sudo docker images -q)
#change owner of volume: sudo chown -R phil src/
