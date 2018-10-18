#!/bin/bash
imageName=test_docker
containerName=test
user=phil

echo Delete old container...
docker rm -f $containerName

echo Run new container...
sudo docker run -d --name $containerName -v "$PWD"/src:/app --rm -i -t $imageName bash
chown -R $user src/
