from framework.controller import *
from framework.config import *
import giveaminute.location as mLocation


class Location(Controller):
    def GET(self, action=None, id=None):
        if (action == 'geojson'):
            return self.getgeojson()
        else:
            return self.not_found()

    def getgeojson(self):
        locationId = self.request('location_id')
        if locationId is None or locationId == '':
            return False
        location = self.orm.query(models.Location).get(locationId)
        if location:
            return location.geometry
        else:
            return False
