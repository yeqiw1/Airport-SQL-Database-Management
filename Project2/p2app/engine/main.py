# p2app/engine/main.py
#
# ICS 33 Spring 2024
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.
import sqlite3
from p2app.events import *
import p2app.engine.continent
import p2app.engine.country
import p2app.engine.region

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.connection = None
        pass


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        try:
            if isinstance(event, OpenDatabaseEvent):
                try:
                    path = event.path()
                    connection = sqlite3.connect(path)
                    self.connection = connection
                    connection.execute('PRAGMA foreign_keys = ON;')
                    yield DatabaseOpenedEvent(path)
                except:
                    yield DatabaseOpenFailedEvent("Sorry, failed to open the database.")

            if isinstance(event, QuitInitiatedEvent):
                yield EndApplicationEvent()

            if isinstance(event, CloseDatabaseEvent):
                yield DatabaseClosedEvent()
            """
            These are for the process of continent related events.
            """
            if isinstance(event, StartContinentSearchEvent):
                yield from p2app.engine.continent.start_continent_search(event, self.connection)

            if isinstance(event, LoadContinentEvent):
                yield from p2app.engine.continent.load_continent(event, self.connection)

            if isinstance(event, SaveNewContinentEvent):
                yield from p2app.engine.continent.save_new_continent(event, self.connection)

            if isinstance(event, SaveContinentEvent):
                yield from p2app.engine.continent.save_continent(event, self.connection)
            """
            These are for the process of country related events.
            """
            if isinstance(event, StartCountrySearchEvent):
                yield from p2app.engine.country.start_country_search(event, self.connection)

            if isinstance(event, LoadCountryEvent):
                yield from p2app.engine.country.load_country(event, self.connection)

            if isinstance(event, SaveNewCountryEvent):
                yield from p2app.engine.country.save_new_country(event, self.connection)

            if isinstance(event, SaveCountryEvent):
                events = p2app.engine.country.save_country(event,self.connection)
                print(type(events))
                yield from events
            """
            These are for the process of region related events.
            """
            if isinstance(event, StartRegionSearchEvent):
                yield from p2app.engine.region.start_region_search(event, self.connection)

            if isinstance(event, LoadRegionEvent):
                yield from p2app.engine.region.load_region(event, self.connection)

            if isinstance(event, SaveNewRegionEvent):
                yield from p2app.engine.region.save_new_region(event, self.connection)

            if isinstance(event, SaveRegionEvent):
                yield from p2app.engine.region.save_region(event, self.connection)
        except:
            yield ErrorEvent("Error.")
