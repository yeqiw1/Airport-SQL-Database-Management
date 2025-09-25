import sqlite3
from p2app.events import *


def start_country_search(event, connection):
    """
    This function search for country, can use name or country code.
    Return a list called events with CountrySearchResultEvent.
    """
    cursor = connection.cursor()
    events = []
    country_code = event.country_code()
    country_name = event.name()
    if country_code is None:
        statement = 'SELECT * FROM country WHERE name = ?;'
        cursor.execute(statement, (country_name,))
    elif country_name is None:
        statement = 'SELECT * FROM country WHERE country_code = ?;'
        cursor.execute(statement, (country_code,))
    else:
        statement = 'SELECT * FROM country WHERE country_code = ? AND name = ?;'
        cursor.execute(statement, (country_code, country_name))

    country_results = cursor.fetchall()
    for country in country_results:
        country = Country(*country)
        events.append(CountrySearchResultEvent(country))
    cursor.close()
    return events


def load_country(event, connection):
    """
    This function load the country according to the id,
    and return the list which contains CountryLoadedEvent.
    """
    cursor = connection.cursor()
    events = []
    country_id = event.country_id()
    statement = 'SELECT * FROM country WHERE country_id = ?;'
    cursor.execute(statement, (country_id,))
    country = cursor.fetchone()
    country_result = Country(*country)
    events.append(CountryLoadedEvent(country_result))
    cursor.close()
    return events

def save_new_country(event, connection):
    """
    This function adds new country into the database tables,
    will return a list containing the new country in form of
    CountrySavedEvent. If failed to add, then will return SaveCountryFailedEvent.
    """
    cursor = connection.cursor()
    events = []
    new_country = event.country()
    the_id, code, name, continent_id, link, keywords = new_country
    link = link or ''

    try:
        statement = 'INSERT INTO country VALUES (?, ?, ?, ?, ?, ?);'
        cursor.execute(statement, (the_id, code, name, continent_id, link, keywords))
        connection.commit()
        new_country = Country(the_id, code, name, continent_id, link, keywords)
        events.append(CountrySavedEvent(new_country))
    except sqlite3.IntegrityError as e:
        reason = f"Failed to save due to duplicated code or invalid id: {str(e)}"
        events.append(SaveCountryFailedEvent(reason))
    return events


def save_country(event, connection):
    """
    This function modify the country exist in the database tables,
    will return a list containing the modified country in form of
    CountrySavedEvent. If failed to add, then will return SaveCountryFailedEvent.
    """
    cursor = connection.cursor()
    events = []
    new_country = event.country()
    the_id, code, name, continent_id, link, keywords = new_country
    link = link or ''

    try:
        statement = 'UPDATE country SET country_code = ?, name = ?, continent_id = ?, wikipedia_link = ?, keywords = ? WHERE country_id = ?;'
        cursor.execute(statement,(code, name, continent_id, link, keywords, the_id))
        connection.commit()
        new_country = Country(the_id, code, name, continent_id, link, keywords)
        events.append(CountrySavedEvent(new_country))
    except sqlite3.IntegrityError as error:
        reason = f"Failed to save due to duplicated code or invalid code: {str(error)}"
        events.append(SaveCountryFailedEvent(reason))
    return events