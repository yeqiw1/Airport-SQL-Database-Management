import sqlite3
from p2app.events import *

def start_region_search(event, connection):
    """
    This function search for region, can use local code, region code or name.
    Return a list called events with RegionSearchResultEvent.
    """
    cursor = connection.cursor()
    events = []
    region_code = event.region_code()
    local_code = event.local_code()
    region_name = event.name()
    if region_code is None and local_code is not None and region_name is not None:
        statement = 'SELECT * FROM region WHERE local_code = ? AND name = ?;'
        cursor.execute(statement, (local_code, region_name))
    elif region_code is None and local_code is None and region_name is not None:
        statement = 'SELECT * FROM region WHERE name = ?;'
        cursor.execute(statement, (region_name,))
    elif region_code is None and local_code is not None and region_name is None:
        statement = 'SELECT * FROM region WHERE local_code = ?;'
        cursor.execute(statement, (local_code,))
    elif region_code is not None and local_code is not None and region_name is not None:
        statement = 'SELECT * FROM region WHERE region_code = ? AND local_code = ? AND name = ?;'
        cursor.execute(statement, (region_code, local_code, region_name))
    elif region_code is not None and local_code is None and region_name is None:
        statement = 'SELECT * FROM region WHERE region_code = ?;'
        cursor.execute(statement, (region_code,))
    elif region_code is not None and local_code is not None and region_name is None:
        statement = 'SELECT * FROM region WHERE region_code = ? AND local_code = ?;'
        cursor.execute(statement, (region_code, local_code))
    elif region_code is not None and local_code is None and region_name is not None:
        statement = 'SELECT * FROM region WHERE region_code = ? AND name = ?;'
        cursor.execute(statement, (region_code, region_name))

    region_results = cursor.fetchall()
    for region in region_results:
        region = Region(*region)
        events.append(RegionSearchResultEvent(region))
    cursor.close()
    return events


def load_region(event, connection):
    """
    This function load the region according to the id,
    and return the list which contains RegionLoadedEvent.
    """
    cursor = connection.cursor()
    events = []
    region_id = event.region_id()
    statement = 'SELECT * FROM region WHERE region_id = ?;'
    cursor.execute(statement, (region_id,))
    region = cursor.fetchone()
    region_result = Region(*region)
    events.append(RegionLoadedEvent(region_result))
    cursor.close()
    return events


def save_new_region(event, connection):
    """
    This function adds new region into the database tables,
    will return a list containing the new region in form of
    RegionSavedEvent. If failed to add, then will return SaveRegionFailedEvent.
    """
    cursor = connection.cursor()
    events = []
    the_id, region_code, local_code, region_name, continent_id, country_id, link, keywords = event.region()
    link = link or ''

    try:
        statement = 'INSERT INTO region VALUES (?, ?, ?, ?, ?, ?, ?, ?);'
        cursor.execute(statement, (the_id, region_code, local_code, region_name, continent_id, country_id, link, keywords))
        connection.commit()
        new_region = Region(the_id, region_code, local_code, region_name, continent_id, country_id, link, keywords)
        events.append(RegionSavedEvent(new_region))
    except sqlite3.IntegrityError as error:
        reason = f"Failed to save due to duplicated code or invalid id: {str(error)}"
        events.append(SaveRegionFailedEvent(reason))
    return events


def save_region(event, connection):
    """
    This function modify the region exist in the database tables,
    will return a list containing the modified region in form of
    RegionSavedEvent. If failed to add, then will return SaveRegionFailedEvent.
    """
    cursor = connection.cursor()
    events = []
    new_region = event.region()
    the_id, region_code, local_code, region_name, continent_id, country_id, link, keywords = new_region
    link = link or ''

    try:
        statement = 'UPDATE region SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? WHERE region_id = ?;'
        cursor.execute(statement, (
        region_code, local_code, region_name, continent_id, country_id, link, keywords,
        the_id))
        connection.commit()
        new_region = Region(the_id, region_code, local_code, region_name, continent_id, country_id,
                            link, keywords)
        events.append(RegionSavedEvent(new_region))
    except sqlite3.IntegrityError as error:
        reason = f"Failed to save due to duplicated code or invalid id: {str(error)}"
        events.append(SaveRegionFailedEvent(reason))
    except Exception as e:
        reason = f"An unexpected error occurred: {str(e)}"
        events.append(SaveRegionFailedEvent(reason))
    return events