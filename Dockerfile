# Use an official Python runtime as a parent image
#FROM python:3.6-slim
FROM ubuntu:18.04

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN yes | apt update
RUN yes | apt install python-pip python3-pip python-dev build-essential 

RUN pip3 install -r requirements.txt
RUN apt-get update
RUN yes | apt-get install libgtk2.0-dev


#Install GDAL
RUN ln -sfn /usr/bin/python3.6 /usr/bin/python
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable
RUN apt update 
RUN yes | apt upgrade
RUN yes | apt install gdal-bin python-gdal python3-gdal

#COCO installation
RUN yes | apt-get install git-core
RUN git clone https://github.com/pdollar/coco.git && cd coco/PythonAPI && make && make install && python setup.py install

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
