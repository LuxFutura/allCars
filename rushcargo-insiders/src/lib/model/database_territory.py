from psycopg import sql

from rich.prompt import IntPrompt

from .classes import Country, Province, Region, City
from .constants import *
from .database import console
from .database_tables import (
    BaseTable,
    uniqueInserted,
    uniqueInsertedMult,
    noCoincidence,
    insertedRow,
    getTable,
)

from ..io.validator import clear


class CountryTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Country Table
    """

    def __init__(self, remoteCursor):
        """
        Country Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Base Table Class
        super().__init__(COUNTRY_TABLENAME, COUNTRY_ID, remoteCursor)

    def __print(self) -> int:
        """
        Method that Prints the Countries Fetched from its Remote Table

        :return: Number of Fetched Countries
        :rtype: int
        """

        # Number of Countries to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("Country", nRows)

        # Add Country Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Phone Prefix", justify="left", max_width=PHONE_PREFIX_NCHAR)

        for item in self._items:
            # Intialize Country from the SQL Row Fetched
            c = Country.fromFetchedItem(item)

            # Add Country Row to Rich Table
            table.add_row(str(c.countryId), c.name, str(c.phonePrefix))

        console.print(table)

        return nRows

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Country to its Remote Table

        :return: SQL Query to Insert a New Country
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(COUNTRY_NAME), sql.Identifier(COUNTRY_PHONE_PREFIX)]
            ),
        )

    def add(self, countryName: str) -> None:
        """
        Method to Insert a New Country to the Country Table

        :param str countryName: Country Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Check if the Country has already been Inserted
        if self.get(COUNTRY_NAME, countryName, False):
            uniqueInserted(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)
            return

        # Ask for the Country Fields
        console.print("\nAdding New Country...", style="caption")
        phonePrefix = IntPrompt.ask("Enter Phone Prefix")

        # Get Query to Insert the New Country
        insertQuery = self.__insertQuery()

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(insertQuery, [countryName, phonePrefix])
            insertedRow(countryName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Countries from its Remote Table based on a Given Field-Value Pair

        :param str field: Country Field that will be Used to Compare in the Country Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not BaseTable._get(self, field, value):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def find(self, field: str, value) -> Country | None:
        """
        Method to Find a Country at its Remote Table based on its Unique Fields

        :param str field: Country Field that will be Used to Compare in the Country Table
        :param value: Unique Value to Compare
        :return: Country Object if Found. Otherwise, ``None``
        :rtype: Country if Found. Otherwise, NoneType
        """

        # Get Country from its Remote Table
        if not self.get(field, value, False):
            return None

        # Get Country Object from the Fetched Item
        return Country.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> int:
        """
        Method that Prints the All the Countries Stored at its Remote Table

        :param str orderBy: Country Field that will be Used to Sort the Country Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Number of Fetched Countries
        :rtype: int
        """

        # Fetch All Countries
        BaseTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Countries
        return self.__print()

    def modify(self, countryId: int, field: str, value) -> None:
        """
        Method to Modify a Country Field to its Remote Table

        :param int countryId: Country ID from its Remote Table
        :param str field: Country Field to Modify
        :param value: Country Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._modify(self, countryId, field, value)

    def remove(self, countryId: int) -> None:
        """
        Method to Remove a Country Row from its Remote Table

        :param int countryId: Country ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._remove(self, countryId)


class ProvinceTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Province Table
    """

    def __init__(self, remoteCursor):
        """
        Province Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Base Table Class
        super().__init__(PROVINCE_TABLENAME, PROVINCE_ID, remoteCursor)

    def __print(self) -> int:
        """
        Method that Prints the Provinces Fetched from its Remote Table

        :return: Number of Fetched Provinces
        :rtype: int
        """

        # Number of Provinces to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("Province", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Country ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Air Forwarder ID", justify="left", max_width=FORWARDER_NCHAR)
        table.add_column(
            "Ocean Forwarder ID", justify="left", max_width=FORWARDER_NCHAR
        )
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        for item in self._items:
            # Intialize Province from the Fetched Item
            p = Province.fromFetchedItem(item)

            # Add Row to Rich Table
            table.add_row(
                str(p.provinceId),
                p.name,
                str(p.countryId),
                str(p.airForwarderId),
                str(p.oceanForwarderId),
                str(p.warehouseId),
            )

        console.print(table)

        return nRows

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Province to its Remote Table

        :return: SQL Query to Insert a New Province
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(PROVINCE_FK_COUNTRY), sql.Identifier(PROVINCE_NAME)]
            ),
        )

    def add(self, countryId: int, provinceName: str) -> None:
        """
        Method to Insert a New Province to the Province Table

        :param int countryId: Country ID at its Remote Table where the Province is Located
        :param str provinceName: Province Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        provinceFields = [PROVINCE_FK_COUNTRY, PROVINCE_NAME]
        provinceValues = [countryId, provinceName]

        # Check if the Province Name has already been Inserted for the Given Country
        if self.getMult(provinceFields, provinceValues, False):
            uniqueInsertedMult(PROVINCE_TABLENAME, provinceFields, provinceValues)
            return

        # Ask for the Province Fields
        console.print("\nAdding New Province...", style="caption")

        # Get Query to Insert the New Province
        query = self.__insertQuery()

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(query, [countryId, provinceName])
            insertedRow(provinceName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Provinces from its Remote Table based on a Given Field-Value Pair

        :param str field: Province Field that will be Used to Compare in the Province Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not BaseTable._get(self, field, value):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        """
        Method to Filter Provinces from its Remote Table based on Some Given Field-Value Pair

        :param list fields: Province Fields that will be Used to Compare in the Province Table
        :param list values: Values to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if not BaseTable._getMult(self, fields, values):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def findMult(self, countryId: int, provinceName: str) -> Province | None:
        """
        Method to Find a Province at its Remote Table based on its Name and the Country ID where it's Located

        :param int countryId: Country ID where the Province is Located
        :param str provinceName: Province Name to Search for
        :return: Province Object if Found. Otherwise, ``None``
        :rtype: Province if Found. Otherwise, NoneType
        """

        # Get Province from its Remote Table
        if not self.getMult(
            [PROVINCE_FK_COUNTRY, PROVINCE_NAME], [countryId, provinceName], False
        ):
            return None

        # Get Province Object from the Fetched Item
        return Province.fromFetchedItem(self._items[0])

    def find(self, provinceId: int) -> Province | None:
        """
        Method to Find a Province at its Remote Table based on its ID

        :param str provinceId: Province ID to Search for
        :return: Province Object if Found. Otherwise, ``None``
        :rtype: Province if Found. Otherwise, NoneType
        """

        # Get Province from its Remote Table
        if not self.get(self._tablePKName, provinceId, False):
            return None

        # Get Province Object from the Fetched Item
        return Province.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> int:
        """
        Method that Prints the All the Provinces Stored at its Remote Table

        :param str orderBy: Province Field that will be Used to Sort the Province Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Number of Fetched Provinces
        :rtype: int
        """

        # Fetch All Provinces
        BaseTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Provinces
        return self.__print()

    def modify(self, provinceId: int, field: str, value) -> None:
        """
        Method to Modify a Province Field to its Remote Table

        :param int provinceId: Province ID from its Remote Table
        :param str field: Province Field to Modify
        :param value: Province Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._modify(self, provinceId, field, value)

    def remove(self, provinceId: int) -> None:
        """
        Method to Remove a Province Row from its Remote Table

        :param int provinceId: Province ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._remove(self, provinceId)


class RegionTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Region Table
    """

    def __init__(self, remoteCursor):
        """
        Region Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Base Table Class
        super().__init__(REGION_TABLENAME, REGION_ID, remoteCursor)

    def __print(self) -> int:
        """
        Method that Prints the Regions Fetched from its Remote Table

        :return: Number of Fetched Regions
        :rtype: int
        """

        # Number of Regions to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("Region", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Province ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        for item in self._items:
            # Intialize Region from the Fetched Item
            r = Region.fromFetchedItem(item)

            # Add Row to Rich Table
            table.add_row(
                str(r.regionId), r.name, str(r.provinceId), str(r.warehouseId)
            )

        console.print(table)

        return nRows

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Region to its Remote Table

        :return: SQL Query to Insert a New Region
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(REGION_FK_PROVINCE), sql.Identifier(REGION_NAME)]
            ),
        )

    def add(self, provinceId: int, regionName: str) -> None:
        """
        Method to Insert a New Region to the Region Table

        :param int provinceId: Province ID at its Remote Table where the Region is Located
        :param str regionName: Region Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        regionFields = [REGION_FK_PROVINCE, REGION_NAME]
        regionValues = [provinceId, regionName]

        # Check if the Region Name has already been Inserted for the Given Province
        if self.getMult(regionFields, regionValues, False):
            uniqueInsertedMult(REGION_TABLENAME, regionFields, regionValues)
            return

        # Ask for the Region Fields
        console.print("\nAdding New Region...", style="caption")

        # Get Query to Insert the New Region
        query = self.__insertQuery()

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(query, [provinceId, regionName])
            insertedRow(regionName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Regions from its Remote Table based on a Given Field-Value Pair

        :param str field: Region Field that will be Used to Compare in the Region Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not BaseTable._get(self, field, value):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        """
        Method to Filter Regions from its Remote Table based on Some Given Field-Value Pair

        :param list fields: Region Fields that will be Used to Compare in the Region Table
        :param list values: Values to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if not BaseTable._getMult(self, fields, values):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def findMult(self, provinceId: int, regionName: str) -> Region | None:
        """
        Method to Find a Region at its Remote Table based on its Name and the Province ID where it's Located

        :param int provinceId: Province ID where the Region is Located
        :param str regionName: Region Name to Search for
        :return: Region Object if Found. Otherwise, ``None``
        :rtype: Region if Found. Otherwise, NoneType
        """

        # Get Region from its Remote Table
        if not self.getMult(
            [REGION_FK_PROVINCE, REGION_NAME], [provinceId, regionName], False
        ):
            return None

        # Get Region Object from the Fetched Item
        return Region.fromFetchedItem(self._items[0])

    def find(self, regionId: int) -> Region | None:
        """
        Method to Find a Region at its Remote Table based on its ID

        :param str regionId: Region ID to Search for
        :return: Region Object if Found. Otherwise, ``None``
        :rtype: Region if Found. Otherwise, NoneType
        """

        # Get Region from its Remote Table
        if not self.get(self._tablePKName, regionId, False):
            return None

        # Get Region Object from the Fetched Item
        return Region.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> int:
        """
        Method that Prints the All the Regions Stored at its Remote Table

        :param str orderBy: Region Field that will be Used to Sort the Region Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Number of Fetched Regions
        :rtype: int
        """

        # Fetch All Regions
        BaseTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Regions
        return self.__print()

    def modify(self, regionId: int, field: str, value) -> None:
        """
        Method to Modify a Region Field to its Remote Table

        :param int regionId: Region ID from its Remote Table
        :param str field: Region Field to Modify
        :param value: Region Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._modify(self, regionId, field, value)

    def remove(self, regionId: int) -> None:
        """
        Method to Remove a Region Row from its Remote Table

        :param int regionId: Region ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._remove(self, regionId)


class CityTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL City Table
    """

    def __init__(self, remoteCursor):
        """
        City Table Remote Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Base Table Class
        super().__init__(CITY_TABLENAME, CITY_ID, remoteCursor)

    def __print(self) -> int:
        """
        Method that Prints the Cities Fetched from its Remote Table

        :return: Number of Fetched Cities
        :rtype: int
        """

        # Number of Cities to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("City", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Region ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        for item in self._items:
            # Intialize City from the Fetched Item
            c = City.fromFetchedItem(item)

            # Add Row to Rich Table
            table.add_row(str(c.cityId), c.name, str(c.regionId), str(c.warehouseId))

        console.print(table)

        return nRows

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New City to its Remote Table

        :return: SQL Query to Insert a New City
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITY_FK_REGION), sql.Identifier(CITY_NAME)]
            ),
        )

    def add(self, regionId: int, cityName: str) -> None:
        """
        Method to Insert a New City to the City Table

        :param int regionId: Region ID at its Remote Table where the City is Located
        :param str cityName: City Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        cityFields = [CITY_FK_REGION, CITY_NAME]
        cityValues = [regionId, cityName]

        # Check if the City Name has already been Inserted for the Given Region
        if self.getMult(cityFields, cityValues, False):
            uniqueInsertedMult(CITY_TABLENAME, cityFields, cityValues)
            return

        # Ask for the City Fields
        console.print("\nAdding New City...", style="caption")

        # Get Query to Insert the New City
        query = self.__insertQuery()

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(query, [regionId, cityName])
            insertedRow(cityName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Cities from its Remote Table based on a Given Field-Value Pair

        :param str field: City Field that will be Used to Compare in the City Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not BaseTable._get(self, field, value):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        """
        Method to Filter Cities from its Remote Table based on Some Given Field-Value Pair

        :param list fields: City Fields that will be Used to Compare in the City Table
        :param list values: Values to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if not BaseTable._getMult(self, fields, values):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def findMult(self, regionId: int, cityName: str) -> City | None:
        """
        Method to Find a City at its Remote Table based on its Name and the Region ID where it's Located

        :param int regionId: Region ID where the City is Located
        :param str cityName: City Name to Search for
        :return: City Object if Found. Otherwise, ``None``
        :rtype: City if Found. Otherwise, NoneType
        """

        # Get City from its Remote Table
        if not self.getMult([CITY_FK_REGION, CITY_NAME], [regionId, cityName], False):
            return None

        # Get City Object from Fetched Item
        return City.fromFetchedItem(self._items[0])

    def find(self, cityId: int) -> City | None:
        """
        Method to Find a City at its Remote Table based on its ID

        :param str cityId: City ID to Search for
        :return: City Object if Found. Otherwise, ``None``
        :rtype: City if Found. Otherwise, NoneType
        """

        # Get City from its Remote Table
        if not self.get(self._tablePKName, cityId, False):
            return None

        # Get City Object from the Fetched Item
        return City.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> int:
        """
        Method that Prints the All the Cities Stored at its Remote Table

        :param str orderBy: City Field that will be Used to Sort the City Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Number of Fetched Cities
        :rtype: int
        """

        # Fetch All Cities
        BaseTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Cities
        return self.__print()

    def modify(self, cityId: int, field: str, value) -> None:
        """
        Method to Modify a City Field to its Remote Table

        :param int cityId: City ID from its Remote Table
        :param str field: City Field to Modify
        :param value: City Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._modify(self, cityId, field, value)

    def remove(self, cityId: int) -> None:
        """
        Method to Remove a City Row from its Remote Table

        :param int cityId: City ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._remove(self, cityId)
