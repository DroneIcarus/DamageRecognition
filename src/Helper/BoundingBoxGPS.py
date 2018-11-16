import json

class BoundingBoxGPS:
    def __init__(self, lat1, long1, lat2, long2):
        #Left Upper Corner
        self.lat1 = lat1
        self.long1 = long1
        #Right Down Corner
        self.lat2 = lat2
        self.long2 = long2

    def toJSON(self):
        return json.dumps(self.__dict__)
