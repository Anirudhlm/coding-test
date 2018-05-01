#!/usr/bin/env python3

"""
USGS (US Geological Survey) publishes various earthquake data as JSON feed. Here’s a feed spanning all domestic earthquakes from the past week:
https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson

Using this JSON feed:
1) identify every earthquake in California from past week,
2) list them chronologically (ascending),
3. and finally output in a format resembling the following e.g.:

2017-07-13T20:43:37+00:00 | 3km NW of Greenville, California | Magnitude: 1
2017-07-13T22:09:53+00:00 | 41km SW of Ferndale, California | Magnitude: 2.76
2017-07-13T22:31:04+00:00 | 11km E of Mammoth Lakes, California | Magnitude: 1.31
2017-07-13T22:32:48+00:00 | 15km SE of Mammoth Lakes, California | Magnitude: 0.92
2017-07-13T22:37:52+00:00 | 12km E of Mammoth Lakes, California | Magnitude: 0.95
2017-07-13T22:45:28+00:00 | 37km SE of Bridgeport, California | Magnitude: 1.7
2017-07-13T22:49:58+00:00 | 8km ENE of Mammoth Lakes, California | Magnitude: 0.92
2017-07-13T22:54:30+00:00 | 3km SE of Atascadero, California | Magnitude: 2.04

----

execute: python3 solution.py

"""

from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime, timezone
import json

class Earthquakes(object):

    def __init__(self, filter_values, filter_type):
        self.usgs_url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson'
        self.usgs_regions_url = 'https://earthquake.usgs.gov/ws/geoserve/regions.json'
        self.filter_values = ['CA', 'California']
        self.filter_type = 'earthquake'
        self.filtered_earthquakes = []
        self.filtered_earthquakes_log = ''

    def _filter_earthquakes(self):
        """Filter features events by type (earthquake) and place (California) by parsing"""
        earthquakes = json.load(urlopen(self.usgs_url))['features']
        # USGS weekly earthquakes api returns data in chronological descending order
        # reversing the list to get chronological ascending order
        earthquakes = earthquakes[::-1]
        # List comprehension to filter features type which are listed as earthquake
        # and parsing state from place to identify location
        self.filtered_earthquakes = [quakes for quakes in earthquakes 
            if quakes['properties']['type'] == self.filter_type
            and quakes['properties']['place'].split(',')[-1].strip() in self.filter_values
            ]
        return self.filtered_earthquakes

    def _filter_earthquakes_by_coordinates(self):
        """Filter for features type (earthquake) and place (California) by USGA regions API"""
        earthquakes = json.load(urlopen(self.usgs_url))['features']
        # USGS weekly earthquakes api returns data in chronological descending order
        # reversing the list to get chronological ascending order
        earthquakes = earthquakes[::-1]
        for quakes in earthquakes:
            location = self._get_location(quakes['geometry']['coordinates'])
            if quakes['properties']['type'] == self.filter_type and location in self.filter_values:
                self.filtered_earthquakes.append(quakes)
        return self.filtered_earthquakes

    def _convert_time(self, unix_time):
        """Converts Epoch time to iso format"""
        unix_time = int(unix_time)
        # dividing unix timestamp by 1000 to convert from milliseconds to seconds
        str_time = datetime.fromtimestamp(unix_time/1000, tz=timezone.utc)
        str_time = str_time.strftime('%Y-%m-%dT%H:%M:%S%z')
        return str_time

    # Alternate approach to get location from latitude & longitude
    def _get_location (self, geometry):
        """Get Location using coordinates from USGA regions API"""
        longitude = geometry[0]
        latitude = geometry[1]
        coordinates = { 'longitude' : longitude, 
            'latitude' : latitude,
            'type': 'neiccatalog'}
        params = urlencode(coordinates)
        location_url = self.usgs_regions_url + '?' + params
        location = json.load(urlopen(location_url))['neiccatalog']['features']
        name = location[0]['properties']['name']
        return name

    def log_earthquakes(self):
        """Log results in correct format"""
        # self._filter_earthquakes()
        self._filter_earthquakes_by_coordinates()
        for i in range(len(self.filtered_earthquakes)):
            time = self._convert_time(self.filtered_earthquakes[i]['properties']['time'])
            place = self.filtered_earthquakes[i]['properties']['place']
            magnitude = str(self.filtered_earthquakes[i]['properties']['mag'])
            self.filtered_earthquakes_log += time + ' | ' + place + ' | magnitude : ' + magnitude
            print (time + ' | ' + place + ' | magnitude : ' + magnitude)
        return

if __name__ == '__main__':
    ca_earthquakes = Earthquakes(filter_values=['CA', 'California'], filter_type='earthquake')
    ca_earthquakes.log_earthquakes()