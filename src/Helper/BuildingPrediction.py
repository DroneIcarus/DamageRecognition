import json
from Helper.BoundingBoxGPS import BoundingBoxGPS
from Helper.ComplexEncoder import ComplexEncoder

class BuildingPrediction:
    def __init__(self, id, boundingBox):
        self.Id = id
        self.BoundingBox = boundingBox

    def toJSON(self):
        return json.dumps(self.reprJSON(), cls=ComplexEncoder)

    def reprJSON(self):
        return dict(Id=self.Id, BoundingBox=self.BoundingBox)
