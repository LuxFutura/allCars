from rich.prompt import Prompt, IntPrompt, Confirm

from .constants import *
from .exceptions import RowNotFound

from ..geocoding.geopy import geoPyGeocoder

from ..io.constants import (
    ADD,
    RM,
    ALL,
    GET,
    MOD,
)
from ..io.validator import *

from ..local_database.database import GeoPyDatabase, GeoPyTables

from ..model.database import db
from ..model.database_tables import uniqueInsertedMult, uniqueInserted
from ..model.database_territory import *

# GeoPy Local Database
localdb = None
tables = None

# Territory Event Handler
territoryEventHandler = None


# Territory Table-related Event Handler
class TerritoryEventHandler:
    # Table Classes
    _countryTable = None
    _provinceTable = None
    _regionTable = None
    _cityTable = None
    _cityAreaTable = None

    # Get Location Messages
    _getCountryMsg = "Enter Country Name"
    _getProvinceMsg = "Enter Province Name"
    _getRegionMsg = "Enter Region Name"
    _getCityMsg = "Enter City Name"
    _getCityAreaMsg = "Enter City Area Name"

    # Constructor
    def __init__(self, db: Database):
        # Global Variables
        global localdb
        global tables

        # Initialize Table Classes
        self._countryTable = CountryTable(db)
        self._provinceTable = ProvinceTable(db)
        self._regionTable = RegionTable(db)
        self._cityTable = CityTable(db)
        self._cityAreaTable = CityAreaTable(db)

        # Initialize GeoPy Local Database
        localdb = GeoPyDatabase()

        # Get GeoPy Local Database Cursor
        cursor = localdb.getCursor()

        # Initialize Local Database Tables Class
        tables = GeoPyTables(cursor)

    # Get Country ID and Name
    def getCountryId(self) -> dict | None:
        # Global Variables
        global localdb

        while True:
            countrySearch = Prompt.ask(self._getCountryMsg)

            # Check Country Name
            isAddressValid(COUNTRY_TABLENAME, COUNTRY_NAME, countrySearch)

            # Initialize Data Dictionary
            data = {}

            # Check if Country Search is Stored in Local Database
            countryNameId = tables.getCountrySearchNameId(countrySearch)
            data[DICT_COUNTRY_NAME_ID] = countryNameId
            countryName = None

            # Check Country Name ID
            if countryNameId != None:
                # Get Country Name from Local Database
                countryName = tables.getCountryName(countryNameId)
                data[DICT_COUNTRY_NAME] = countryName
            else:
                # Get Country Name from GeoPy API based on the Name Provided
                try:
                    countryName = geoPyGeocoder.getCountry(countrySearch)
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                data[DICT_COUNTRY_NAME] = countryName

                # Store Country Search in Local Database
                tables.addCountry(countrySearch, countryName)

                # Get Country Name ID from Local Database
                data[DICT_COUNTRY_NAME_ID] = tables.getCountryNameId(countryName)

            break

        # Get Country
        c = self._countryTable.find(COUNTRY_NAME, countryName)

        if c == None:
            raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

        # Set Country ID to Data Dictionary
        data[DICT_COUNTRY_ID] = c.countryId

        return data

    # Get Province ID based on its Name and the Country ID where it's Located
    def getProvinceId(self) -> dict | None:
        # Global Variables
        global localdb

        # Get Country ID
        data = self.getCountryId()

        while True:
            provinceSearch = Prompt.ask(self._getProvinceMsg)

            # Check Province Name
            isAddressValid(PROVINCE_TABLENAME, PROVINCE_NAME, provinceSearch)

            # Check if Province Search is Stored in Local Database
            provinceNameId = tables.getProvinceSearchNameId(
                data[DICT_COUNTRY_NAME_ID], provinceSearch
            )
            data[DICT_PROVINCE_NAME_ID] = provinceNameId
            provinceName = None

            # Check Province Name ID
            if provinceNameId != None:
                # Get Province Name from Local Database
                provinceName = tables.getProvinceName(provinceNameId)
                data[DICT_PROVINCE_NAME] = provinceName
            else:
                # Get Province Name from GeoPy API based on the Name Provided
                try:
                    provinceName = geoPyGeocoder.getProvince(data, provinceSearch)
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                data[DICT_PROVINCE_NAME] = provinceName

                # Store Province Search at Local Database
                tables.addProvince(
                    data[DICT_COUNTRY_NAME_ID], provinceSearch, provinceName
                )

                # Get Province Name ID from Local Database
                data[DICT_PROVINCE_NAME_ID] = tables.getProvinceNameId(
                    data[DICT_COUNTRY_NAME_ID], provinceName
                )

            break

        # Get Province
        p = self._provinceTable.find(data[DICT_COUNTRY_ID], provinceName)

        if p == None:
            raise RowNotFound(PROVINCE_TABLENAME, PROVINCE_NAME, provinceName)

        # Drop Country ID and Country Name ID from Data Dictionary
        data.pop(DICT_COUNTRY_ID)
        data.pop(DICT_COUNTRY_NAME_ID)

        # Set Province ID to Data Dictionary
        data[DICT_PROVINCE_ID] = p.provinceId

        return data

    # Get Region ID based on its Name and the Province ID where it's Located
    def getRegionId(self) -> dict | None:
        # Global Variables
        global localdb

        # Get Province ID
        data = self.getProvinceId()

        while True:
            regionSearch = Prompt.ask(self._getRegionMsg)

            # Check Region Name
            isAddressValid(REGION_TABLENAME, REGION_NAME, regionSearch)

            # Check if Region Search is Stored in Local Database
            regionNameId = tables.getRegionSearchNameId(
                data[DICT_PROVINCE_NAME_ID], regionSearch
            )
            data[DICT_REGION_NAME_ID] = regionNameId
            regionName = None

            # Check Region Name ID
            if regionNameId != None:
                # Get Region Name from Local Database
                regionName = tables.getRegionName(regionNameId)
                data[DICT_REGION_NAME] = regionName
            else:
                # Get Region Name from GeoPy API based on the Name Provided
                try:
                    regionName = geoPyGeocoder.getRegion(data, regionSearch)
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                data[DICT_REGION_NAME] = regionName

                # Store Region Search in Local Database
                tables.addRegion(data[DICT_PROVINCE_NAME_ID], regionSearch, regionName)

                # Get Region Name ID from Local Database
                data[DICT_REGION_NAME_ID] = tables.getRegionNameId(
                    data[DICT_PROVINCE_NAME_ID], regionName
                )

            break

        # Get Region
        r = self._regionTable.find(data[DICT_PROVINCE_ID], regionName)

        if r == None:
            raise RowNotFound(REGION_TABLENAME, REGION_NAME, regionName)

        # Drop Province ID and Province Name ID from Data Dictionary
        data.pop(DICT_PROVINCE_ID)
        data.pop(DICT_PROVINCE_NAME_ID)

        # Set Region ID to Data Dictionary
        data[DICT_REGION_ID] = r.regionId

        return data

    # Get City ID based on its Name and the Region ID where it's Located
    def getCityId(self) -> dict | None:
        # Global Variables
        global localdb

        # Get Region ID
        data = self.getRegionId()

        while True:
            citySearch = Prompt.ask(self._getCityMsg)

            # Check City Name
            isAddressValid(CITY_TABLENAME, CITY_NAME, citySearch)

            # Check if City Search is Stored in Local Database
            cityNameId = tables.getCitySearchNameId(
                data[DICT_REGION_NAME_ID], citySearch
            )
            data[DICT_CITY_NAME_ID] = cityNameId
            cityName = None

            # Check City Name ID
            if cityNameId != None:
                # Get City Name from Local Database
                cityName = tables.getCityName(cityNameId)
                data[DICT_CITY_NAME] = cityName
            else:
                # Get City Name from GeoPy API based on the Name Provided
                try:
                    cityName = geoPyGeocoder.getCity(
                        data,
                        citySearch,
                    )
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                data[DICT_CITY_NAME] = cityName

                # Store City Search at Local Database
                tables.addCity(data[DICT_REGION_NAME_ID], citySearch, cityName)

                # Get City Name ID from Local Database
                data[DICT_CITY_NAME_ID] = tables.getCityNameId(
                    data[DICT_REGION_NAME_ID], cityName
                )

            break

        # Get City
        c = self._cityTable.find(data[DICT_REGION_ID], cityName)

        if c == None:
            raise RowNotFound(CITY_TABLENAME, CITY_NAME, cityName)

        # Drop Region ID and Region Name ID from Data Dictionary
        data.pop(DICT_REGION_ID)
        data.pop(DICT_REGION_NAME_ID)

        # Set City ID to Data Dictionary
        data[DICT_CITY_ID] = c.cityId

        return data

    # Get City Area ID based on its Name and the City ID where it's Located
    def getCityAreaId(self) -> dict | None:
        # Global Variables
        global localdb

        # Get City ID
        data = self.getCityId()

        while True:
            areaSearch = Prompt.ask(self._getCityAreaMsg)

            # Check City Area Name
            isAddressValid(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaSearch)

            # Check if City Area Search is Stored in Local Database
            areaNameId = tables.getCityAreaSearchNameId(
                data[DICT_CITY_NAME_ID], areaSearch
            )
            data[DICT_CITY_AREA_NAME_ID] = areaNameId
            areaName = None

            # Check City Name ID
            if areaNameId != None:
                # Get City Name from Local Database
                areaName = tables.getCityAreaName(areaNameId)
                data[DICT_CITY_AREA_NAME] = areaName
            else:
                # Get City Area Name from GeoPy API based on the Name Provided
                try:
                    areaName = geoPyGeocoder.getCityArea(
                        data,
                        areaSearch,
                    )
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                data[DICT_CITY_AREA_NAME] = areaName

                # Store City Area Search at Local Database
                tables.addCityArea(data[DICT_CITY_NAME_ID], areaSearch, areaName)

                # Get City Area Name ID from Local Database
                data[DICT_CITY_AREA_NAME_ID] = tables.getCityAreaNameId(
                    data[DICT_CITY_NAME_ID], areaName
                )

            break

        # Get City Area
        a = self._cityAreaTable.find(data[DICT_CITY_ID], areaName)

        if a == None:
            raise RowNotFound(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaName)

        # Drop City ID and City Name ID from Data Dictionary
        data.pop(DICT_CITY_ID)
        data.pop(DICT_CITY_NAME_ID)

        # Set City Area ID to Data Dictionary
        data[DICT_CITY_AREA_ID] = a.areaId

        return data

    # Get Place Coordinates
    def getPlaceCoordinates(self, msg: str) -> dict | None:
        # Global Variables

        # Get City Area ID
        data = self.getCityAreaId()

        while True:
            try:
                # Get Place Name to Search
                placeSearch = Prompt.ask(msg)

                # Check Place Search
                isPlaceNameValid(placeSearch)

                # Get Place Coordinates from GeoPy API based on the Data Provided
                coords = geoPyGeocoder.getPlaceCoordinates(data, placeSearch)

                return coords

            # Handle LocationError Exception
            except Exception as err:
                console.print(err, style="warning")
                continue

    # Get All Table Handler
    def _allHandler(self, tableName: str) -> None:
        sortBy = None

        # Asks if the User wants to Print it in Descending Order
        desc = Confirm.ask(ALL_DESC_MSG)

        if tableName == COUNTRY_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._countryTable.all(sortBy, desc)

        elif tableName == PROVINCE_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[
                    PROVINCE_ID,
                    PROVINCE_FK_COUNTRY,
                    PROVINCE_NAME,
                    PROVINCE_FK_AIR_FORWARDER,
                    PROVINCE_FK_OCEAN_FORWARDER,
                ],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._provinceTable.all(sortBy, desc)

        elif tableName == REGION_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[
                    REGION_ID,
                    REGION_FK_PROVINCE,
                    REGION_NAME,
                    REGION_FK_WAREHOUSE,
                ],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._regionTable.all(sortBy, desc)

        elif tableName == CITY_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._cityTable.all(sortBy, desc)

        elif tableName == CITY_AREA_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[CITY_AREA_ID, CITY_AREA_FK_CITY, CITY_AREA_NAME],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._cityAreaTable.all(sortBy, desc)

    # Get Table Handler
    def _getHandler(self, tableName: str) -> None:
        field = value = None

        if tableName == COUNTRY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Prompt to Ask the Value to be Compared
            if field == COUNTRY_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._countryTable.get(field, value)

        elif tableName == PROVINCE_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[
                    PROVINCE_ID,
                    PROVINCE_FK_COUNTRY,
                    PROVINCE_NAME,
                    PROVINCE_FK_AIR_FORWARDER,
                    PROVINCE_FK_OCEAN_FORWARDER,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == PROVINCE_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._provinceTable.get(field, value)

        elif tableName == REGION_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[
                    REGION_ID,
                    REGION_FK_PROVINCE,
                    REGION_NAME,
                    REGION_FK_WAREHOUSE,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == REGION_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._regionTable.get(field, value)

        elif tableName == CITY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME],
            )

            # Prompt to Ask the Value to be Compared
            if field == CITY_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._cityTable.get(field, value)

        elif tableName == CITY_AREA_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[CITY_AREA_ID, CITY_AREA_FK_CITY, CITY_AREA_NAME],
            )

            # Prompt to Ask the Value to be Compared
            if field == CITY_AREA_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._cityAreaTable.get(field, value)

    # Modify Row from Table Handler
    def _modHandler(self, tableName: str) -> None:
        field = value = None

        if tableName == COUNTRY_TABLENAME:
            # Ask for Country ID to Modify
            countryId = IntPrompt.ask("\nEnter Country ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(MOD_FIELD_MSG, choices=[COUNTRY_PHONE_PREFIX])

            # Prompt to Ask the New Value
            if field == COUNTRY_PHONE_PREFIX:
                value = str(IntPrompt.ask(MOD_VALUE_MSG))

            # Modify Country
            self._countryTable.modify(countryId, field, value)

        elif tableName == PROVINCE_TABLENAME:
            # Ask for Province ID to Modify
            provinceId = IntPrompt.ask("\nEnter Province ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._provinceTable.get(PROVINCE_ID, provinceId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[PROVINCE_FK_AIR_FORWARDER, PROVINCE_FK_OCEAN_FORWARDER],
            )

            # Prompt to Ask the New Value
            if (
                field == PROVINCE_FK_AIR_FORWARDER
                or field == PROVINCE_FK_OCEAN_FORWARDER
            ):
                value = str(IntPrompt.ask(MOD_VALUE_MSG))

            # TO DEVELOP: CHECK AND CONFIRM FORWARDERS

            # Modify Province
            self._provinceTable.modify(provinceId, field, value)

        elif tableName == REGION_TABLENAME:
            # Ask for Region ID to Modify
            regionId = IntPrompt.ask("\nEnter Region ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[REGION_FK_WAREHOUSE],
            )

            # Prompt to Ask the New Value
            if field == REGION_FK_WAREHOUSE:
                value = str(IntPrompt.ask(MOD_VALUE_MSG))

            # TO DEVELOP: CHECK AND CONFIRM WAREHOUSE

            # Modify Region
            self._regionTable.modify(regionId, field, value)

        elif tableName == CITY_TABLENAME:
            console.print(MOD_NOTHING_MSG, style="warning")

        elif tableName == CITY_AREA_TABLENAME:
            # Ask for City Area ID to Modify
            areaId = IntPrompt.ask("\nEnter City Area ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._cityTable.get(CITY_AREA_ID, areaId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[CITY_AREA_DESCRIPTION],
            )

            # Prompt to Ask the New Value
            if field == CITY_AREA_DESCRIPTION:
                value = Prompt.ask(MOD_VALUE_MSG)

                # Check City Area Description
                isAddressValid(tableName, field, value)

            # Modify City Area
            self._cityAreaTable.modify(areaId, field, value)

    # Add Row to Table Handler
    def _addHandler(self, tableName: str) -> None:
        # Global Variables
        global localdb

        # Location Dictionary
        data = None

        while True:
            if tableName == COUNTRY_TABLENAME:
                # Asks for Country Fields
                countrySearch = Prompt.ask(self._getCountryMsg)
                phonePrefix = IntPrompt.ask("Enter Phone Prefix")

                # Check Country Name
                isAddressValid(tableName, COUNTRY_NAME, countrySearch)

                # Check if Country is Stored in Local Database
                countryNameId = tables.getCountrySearchNameId(countrySearch)
                countryName = None

                # Check Country Name ID
                if countryNameId != None:
                    # Get Country Name from Local Database
                    countryName = tables.getCountryName(countryNameId)
                else:
                    # Get Country Name from GeoPy API based on the Name Provided
                    countryName = geoPyGeocoder.getCountry(countrySearch)

                    # Store Country Search in Local Database
                    tables.addCountry(countrySearch, countryName)

                # Check if Country Name has already been Inserted
                if self._countryTable.get(COUNTRY_NAME, countryName, False):
                    uniqueInserted(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)
                    return

                # Insert Country
                self._countryTable.add(Country(countryName, phonePrefix))

            elif tableName == PROVINCE_TABLENAME:
                # Asks for Province Fields
                if data == None:
                    data = self.getCountryId()

                provinceSearch = Prompt.ask(self._getProvinceMsg)

                # Check Province Name
                isAddressValid(tableName, PROVINCE_NAME, provinceSearch)

                # Check if Province is Stored in Local Database
                provinceNameId = tables.getProvinceSearchNameId(
                    data[DICT_COUNTRY_NAME_ID], provinceSearch
                )
                provinceName = None

                # Check Province Name ID
                if provinceNameId != None:
                    # Get Province Name from Local Database
                    provinceName = tables.getProvinceName(provinceNameId)
                else:
                    # Get Province Name from GeoPy API based on the Name Provided
                    provinceName = geoPyGeocoder.getProvince(data, provinceSearch)

                    # Store Province Search in Local Database
                    tables.addProvince(
                        data[DICT_COUNTRY_NAME_ID], provinceSearch, provinceName
                    )

                provinceFields = [PROVINCE_FK_COUNTRY, PROVINCE_NAME]
                provinceValues = [data[DICT_COUNTRY_ID], provinceName]

                # Check if Province Name has already been Inserted for the Given Country
                if self._provinceTable.getMult(provinceFields, provinceValues, False):
                    uniqueInsertedMult(
                        PROVINCE_TABLENAME, provinceFields, provinceValues
                    )
                    return

                # Insert Province
                self._provinceTable.add(Province(provinceName, data[DICT_COUNTRY_ID]))

            elif tableName == REGION_TABLENAME:
                # Asks for Region Fields
                if data == None:
                    data = self.getProvinceId()

                regionSearch = Prompt.ask(self._getRegionMsg)

                # Check Region Name
                isAddressValid(tableName, REGION_NAME, regionSearch)

                # Check if Region is Stored in Local Database
                regionNameId = tables.getRegionSearchNameId(
                    data[DICT_PROVINCE_NAME_ID], regionSearch
                )
                regionName = None

                # Check Region Name ID
                if regionNameId != None:
                    # Get Region Name from Local Database
                    regionName = tables.getRegionName(regionNameId)
                else:
                    # Get Region Name from GeoPy API based on the Name Provided
                    regionName = geoPyGeocoder.getRegion(data, regionSearch)

                    # Store Region Search in Local Database
                    tables.addRegion(
                        data[DICT_PROVINCE_NAME_ID], regionSearch, regionName
                    )

                regionFields = [REGION_FK_PROVINCE, REGION_NAME]
                regionValues = [data[DICT_PROVINCE_ID], regionName]

                # Check if Region Name has already been Inserted for the Given Province
                if self._regionTable.getMult(regionFields, regionValues, False):
                    uniqueInsertedMult(REGION_TABLENAME, regionFields, regionValues)
                    return

                # Insert Region
                self._regionTable.add(Region(regionName, data[DICT_PROVINCE_ID]))

            elif tableName == CITY_TABLENAME:
                # Asks for City Fields
                if data == None:
                    data = self.getRegionId()

                citySearch = Prompt.ask(self._getCityMsg)

                # Check City Name
                isAddressValid(tableName, CITY_NAME, citySearch)

                # Check if City is Stored in Local Database
                cityNameId = tables.getCitySearchNameId(
                    data[DICT_REGION_NAME_ID], citySearch
                )
                cityName = None

                # Check City Name ID
                if cityNameId != None:
                    # Get City Name from Local Database
                    cityName = tables.getCityName(cityNameId)
                else:
                    # Get City Name from GeoPy API based on the Name Provided
                    cityName = geoPyGeocoder.getCity(data, citySearch)

                    # Store City Search in Local Database
                    tables.addCity(data[DICT_REGION_NAME_ID], citySearch, cityName)

                cityFields = [CITY_FK_REGION, CITY_NAME]
                cityValues = [data[DICT_REGION_ID], cityName]

                # Check if City Name has already been Inserted for the Given Province
                if self._cityTable.getMult(cityFields, cityValues, False):
                    uniqueInsertedMult(CITY_TABLENAME, cityFields, cityValues)
                    return

                # Insert City
                self._cityTable.add(City(cityName, data[DICT_REGION_ID]))

            elif tableName == CITY_AREA_TABLENAME:
                # Asks for City Area Fields
                if data == None:
                    data = self.getCityId()

                areaSearch = Prompt.ask(self._getCityAreaMsg)
                areaDescription = Prompt.ask("Enter City Area Description")

                # Check City Area Name and Description
                isAddressValid(tableName, CITY_AREA_NAME, areaSearch)
                isAddressValid(tableName, CITY_AREA_DESCRIPTION, areaDescription)

                # Check if City Area is Stored in Local Database
                areaNameId = tables.getCityAreaSearchNameId(data, areaSearch)
                areaName = None

                # Check City Area Name ID
                if areaNameId != None:
                    # Get City Area Name from Local Database
                    areaName = tables.getCityAreaName(areaNameId)
                else:
                    # Get City Area Name from GeoPy API based on the Name Provided
                    areaName = geoPyGeocoder.getCityArea(data, areaSearch)

                    # Store City Area Search in Local Database
                    tables.addCityArea(data[DICT_CITY_NAME_ID], areaSearch, areaName)

                areaFields = [CITY_AREA_FK_CITY, CITY_AREA_NAME]
                areaValues = [data[DICT_CITY_ID], areaName]

                # Check if City Area Name has already been Inserted for the Given City
                if self._cityAreaTable.getMult(areaFields, areaValues, False):
                    uniqueInsertedMult(CITY_AREA_TABLENAME, areaFields, areaValues)
                    return

                # Insert City Area
                self._cityAreaTable.add(
                    CityArea(areaName, areaDescription, data[DICT_CITY_ID])
                )

            # Ask to Add More
            if not Confirm.ask(ADD_MORE_MSG):
                break

    # Remove Row from Table Handler
    def _rmHandler(self, tableName: str) -> None:
        if tableName == COUNTRY_TABLENAME:
            # Ask for Country ID to Remove
            countryId = IntPrompt.ask("\nEnter Country ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._countryTable.remove(countryId)

        elif tableName == PROVINCE_TABLENAME:
            # Ask for Province ID to Remove
            provinceId = IntPrompt.ask("\nEnter Province ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._provinceTable.get(PROVINCE_ID, provinceId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._provinceTable.remove(provinceId)

        elif tableName == REGION_TABLENAME:
            # Ask for Region ID to Remove
            regionId = IntPrompt.ask("\nEnter Region ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._regionTable.remove(regionId)

        elif tableName == CITY_TABLENAME:
            # Ask for City ID to Remove
            cityId = IntPrompt.ask("\nEnter City ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._cityTable.get(CITY_ID, cityId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._cityTable.remove(cityId)

        elif tableName == CITY_AREA_TABLENAME:
            # Ask for City Area ID to Remove
            areaId = IntPrompt.ask("\nEnter City Area ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._cityAreaTable.get(CITY_AREA_ID, areaId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._cityAreaTable.remove(areaId)

    # Territory Event Handler
    def handler(self, action: str, tableName: str) -> None:
        # Clear Terminal
        clear()

        if action == ALL:
            self._allHandler(tableName)

        elif action == GET:
            self._getHandler(tableName)

        elif action == MOD:
            self._modHandler(tableName)

        elif action == ADD:
            self._addHandler(tableName)

        elif action == RM:
            self._rmHandler(tableName)


# Initialize Territory Event Handler
territoryEventHandler = TerritoryEventHandler(db)