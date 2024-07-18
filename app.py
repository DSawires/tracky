from datetime import datetime
import sqlite3
from flask import Flask, g, request
from geopy import distance


app = Flask(__name__)
DATABASE = 'database.database'

def get_database():
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = sqlite3.connect(DATABASE)
    return database

@app.teardown_appcontext
def close_connection(exception):
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()

def create_table():
    database = get_database()
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            trackerID INTEGER REFERENCES trackers(trackerID),
            lat REAL,
            long REAL,
            timestamp TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trackers (
            trackerID INTEGER PRIMARY KEY AUTOINCREMENT,
            tracker_name TEXT UNIQUE
        )
    ''')
    database.commit()

with app.app_context():
    create_table()

@app.route('/', methods=['GET'])
def running():
    return {"status": "running"}

@app.route('/location/<tracker_id>', methods=['GET'])
def location(tracker_id):
    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        'SELECT lat, long FROM locations WHERE trackerID = ? ORDER BY timestamp DESC LIMIT 1',
        (tracker_id,))
    locations = cursor.fetchall()
    return {"locations": locations}

@app.route('/location_update', methods=['POST'])
def location_update():
    database = get_database()
    data = request.get_json()

    tracker_id = float(data['id'])
    latitude = float(data['latitude'])
    longtitude = float(data['longtitude'])
    cursor = database.cursor()
    cursor.execute(
        'INSERT INTO locations (trackerID, lat, long, timestamp) VALUES (?, ?, ?, ?)',
        (tracker_id, latitude, longtitude, datetime.now()))
    database.commit()
    cursor.execute(
        'SELECT lat, long FROM locations WHERE trackerID = ? ORDER BY timestamp DESC LIMIT 2', 
        (tracker_id,))
    locations = cursor.fetchmany(2)
    if len(locations) < 2:
        return {"distance": 0}
    location1 = locations[0]
    location2 = locations[1]

    moved = distance.distance(location1, location2).km
    return {"distance": moved}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
