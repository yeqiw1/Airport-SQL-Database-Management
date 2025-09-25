import sqlite3
from p2app.events import *

def start_continent_search(event, connection):
    """
    This function search for continent, can use name or continent code.
    Return a list called events with ContinentSearchResultEvent.
    """
    cursor = connection.cursor()
    events = []
    continent_code = event.continent_code()
    continent_name = event.name()
    if continent_code is None:
        statement = 'SELECT * FROM continent WHERE name = ?;'
        cursor.execute(statement, (continent_name,))
    elif continent_name is None:
        statement = 'SELECT * FROM continent WHERE continent_code = ?;'
        cursor.execute(statement, (continent_code,))
    else:
        statement = 'SELECT * FROM continent WHERE continent_code = ? AND name = ?;'
        cursor.execute(statement, (continent_code, continent_name))

    continent_results = cursor.fetchall()
    for continent in continent_results:
        continent = Continent(*continent)
        events.append(ContinentSearchResultEvent(continent))
    cursor.close()
    return events


def load_continent(event, connection):
    """
    This function load the continent according to the id,
    and return the list which contains ContinentLoadedEvent.
    """
    cursor = connection.cursor()
    events = []
    continent_id = event.continent_id()
    statement = 'SELECT * FROM continent WHERE continent_id = ?;'
    cursor.execute(statement, (continent_id,))
    continent = cursor.fetchone()
    continent_result = Continent(*continent)
    events.append(ContinentLoadedEvent(continent_result))
    cursor.close()
    return events


def save_new_continent(event, connection):
    """
    This function adds new continent into the database tables,
    will return a list containing the new continent in form of
    ContinentSavedEvent. If failed to add, then will return SaveContinentFailedEvent.
    """
    cursor = connection.cursor()
    events = []
    continent_id, continent_code, continent_name = event.continent()

    try:
        statement = 'INSERT INTO continent VALUES (?, ?, ?);'
        cursor.execute(statement, (continent_id, continent_code, continent_name))
        connection.commit()
        new_continent = Continent(continent_id, continent_code, continent_name)
        events.append(ContinentSavedEvent(new_continent))
    except sqlite3.IntegrityError as error:
        reason = f"Failed to save due to duplicated continent code: {str(error)}"
        events.append(SaveContinentFailedEvent(reason))
    return events


def save_continent(event, connection):
    """
    This function modify the continent exist in the database tables,
    will return a list containing the modified continent in form of
    ContinentSavedEvent. If failed to add, then will return SaveContinentFailedEvent.
    """
    cursor = connection.cursor()
    events = []
    new_continent = event.continent()
    continent_id, continent_code, continent_name = new_continent

    try:
        statement = 'UPDATE continent SET continent_code = ?, name = ? WHERE continent_id = ?;'
        cursor.execute(statement,
                       (continent_code, continent_name, continent_id))
        connection.commit()
        new_continent = Continent(continent_id, continent_code, continent_name)
        events.append(ContinentSavedEvent(new_continent))
    except sqlite3.IntegrityError as error:
        reason = f"Failed to save due to duplicated continent code or other database error: {str(error)}"
        events.append(SaveContinentFailedEvent(reason))
    except Exception as e:
        events.append(SaveContinentFailedEvent(f"An unexpected error occurred: {str(e)}"))
    return events