from Helper.BoundingBoxGPS import BoundingBoxGPS

class BuildingPrediction:
    def __init__(self, id, boundingBox):
        self.Id = id
        self.BoundingBox = boundingBox

    def toJSON(self):
        return {"Id":self.Id, "BoundingBox": self.BoundingBox.toJSON()}
