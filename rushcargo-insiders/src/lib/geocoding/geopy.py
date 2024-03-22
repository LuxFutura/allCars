from geopy.geocoders import Nominatim

from .constants import *
from ..model.exceptions import *

from ..controller.constants import *


# GeoPy Geocoder Class
class GeoPyGeocoder:
    # Geolocator
    _geolocator = None

    # Constructor
    def __init__(self, userAgent: str, user: str):
        # Initialize Geolocator
        self._geolocator = Nominatim(user_agent=f"{userAgent}-{user}", timeout=5)

    # Get Name
    def __getName(self, locationRaw: dict):
        return locationRaw[NOMINATIM_NAME]

    # Get Country Name
    def getCountry(self, search: str) -> str | None:
        # Get Country Location
        location = self._geolocator.geocode(search)

        # Check if it's a Country
        try:
            # Get Country Name
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_COUNTRY:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(search, NOMINATIM_COUNTRY)

    # Get Region Name
    def getRegion(self, location: dict, region: str) -> str | None:
        # Get Region Location
        location = self._geolocator.geocode(
            ", ".join([region, location[DICT_COUNTRY_NAME]])
        )

        # Check if it's a Region
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(region, NOMINATIM_REGION)

    # Get Subregion Name
    def getSubregion(self, location: dict, subregion: str) -> str | None:
        # Get Subregion Location
        location = self._geolocator.geocode(
            ", ".join(
                [
                    subregion,
                    location[DICT_REGION_NAME],
                    location[DICT_COUNTRY_NAME],
                ]
            )
        )

        # Check if it's a Subregion:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_SUBREGION:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(subregion, NOMINATIM_SUBREGION)

    # Get City Name
    def getCity(self, location: dict, city: str) -> str | None:
        # Get City Location
        location = self._geolocator.geocode(
            ", ".join(
                [
                    city,
                    location[DICT_SUBREGION_NAME],
                    location[DICT_REGION_NAME],
                    location[DICT_COUNTRY_NAME],
                ]
            )
        )

        # Check if it's a City:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(city, NOMINATIM_CITY)

    # Get City Area Name
    def getCityArea(self, location: dict, cityArea: str) -> str | None:
        # Get City Area Location
        location = self._geolocator.geocode(
            ", ".join(
                [
                    cityArea,
                    location[DICT_CITY_NAME],
                    location[DICT_SUBREGION_NAME],
                    location[DICT_REGION_NAME],
                    location[DICT_COUNTRY_NAME],
                ]
            )
        )

        # Check if it's a City Area:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY_AREA:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(cityArea, NOMINATIM_CITY_AREA)


# Initialize GeoPy Geocoder
def initGeoPyGeocoder(userAgent: str, user: str) -> GeoPyGeocoder:
    return GeoPyGeocoder(userAgent, user)