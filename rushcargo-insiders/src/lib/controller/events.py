import logging

from rich.prompt import Confirm
from rich.logging import RichHandler

from .constants import END_MSG
from .locationEvents import LocationEventHandler

from ..io.arguments import getEventHandlerArguments
from ..io.constants import TABLE_LOCATION_CMD
from ..io.validator import clear

from ..model.database import Database
from ..model.database_tables import console


# Get Rich Logger
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("rich")


class EventHandler:
    """
    Class that Handles All the Events
    """

    # Database Connection
    __c = None

    # Event Handlers
    __locationEventHandler = None

    def __init__(self, db: Database, user: str, ORSApiKey: str):
        """
        Event Handler Class Constructor

        :param Database db: Database Object of the Current Connection with the Remote Database
        :param str user: Remote Database Role Name
        :param str ORSApiKey: Open Routing Service API Key
        """

        # Store Database Connection Cursor
        self.__c = db.getCursor()

        # Initialize Location Event Handler
        self.__locationEventHandler = LocationEventHandler(self.__c, user, ORSApiKey)

    def handler(self, action: str, tableGroup: str, tableName: str) -> None:
        """
        Main Handler of ``add``, ``all``, ``get``, ``mod`` and ``rm`` Commands

        :param str action: Command (``add``, ``all``, ``get``, ``mod`` or ``rm``)
        :param str tableGroup: Group of Tables at Remote Database that are Similar at their Model Design-Level
        :param str tableName: Table Name at Remote Database
        :return: Nothing
        :rtype: NoneType
        """

        while True:
            try:
                # Clear Terminal
                clear()

                # Check if it's a Location-related Table
                if tableGroup == TABLE_LOCATION_CMD:
                    # Call Location Event Handler
                    self.__locationEventHandler.handler(action, tableName)

                # Ask to Change the Command
                if Confirm.ask("\nDo you want to Continue with this Command?"):
                    # Clear Terminal
                    clear()
                    continue

                arguments = getEventHandlerArguments()

                # Check if the User wants to Exit the Program
                if arguments == None:
                    break

                # Get Arguments
                action, tableGroup, tableName = arguments

            # End Program
            except KeyboardInterrupt:
                console.print(END_MSG, style="warning")
                return

            except Exception as err:
                console.print(err, style="warning")
                continue
