#!/bin/bash
imageName=icarus_image
containerName=launch_icarus

echo Delete old container...
docker rm -f $containerName

echo Run new container...
sudo docker run -d --name $containerName -v "$PWD"/src:/app --rm -i -t $imageName bash
#sudo docker attach $containerName

docker exec -it $containerName python app.py icarus