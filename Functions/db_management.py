#from Functions.custom_metrics import *
import sqlite3 

tables = ["users", "playlists",  "user_tracks", "user_artists", "streaming_info", "tracks", "artists", "albums"]
columns_list = [["user_id INTEGER PRIMARY KEY", "username VARCHAR NOT NULL"],
                ["playlist_id INTEGER PRIMARY KEY", "playlist_uri_id VARCHAR UNQIUE NOT NULL", "track_id INTEGER NOT NULL", "user_id INTEGER NOT NULL"],
                ["user_id INTEGER PRIMARY KEY", "track_id INTEGER UNIQUE NOT NULL", "ms_listened INTEGER NOT NULL"],
                ["user_id INTEGER PRIMARY KEY", "artist_id INTEGER UNIQUE NOT NULL", "listening_type VARCHAR NOT NULL"],
                ["stream_id INTEGER PRIMARY KEY", "user_id INTEGER NOT NULL", "track_id INTEGER NOT NULL", "timestamp VARCHAR NOT NULL", "ms_played INTEGER NOT NULL", "reason_start VARCHAR", "reason_end VARCHAR", 
                    "shuffle VARCHAR", "skipped VARCHAR", "platform VARCHAR", "country VARCHAR", "offline VARCHAR", "offline_timestamp VARCHAR", "incognito_mode VARCHAR", "episode_name VARCHAR", "episode_show VARCHAR", "episode_id VARCHAR"],
                ["track_id INTEGER PRIMARY KEY", "track_uri_id VARCHAR UNIQUE NOT NULL", "artist_id INTEGER NOT NULL", "album_id INTEGER NOT NULL", "song_name VARCHAR NOT NULL", "duration INTEGER NOT NULL", "main_id INTEGER NOT NULL"], 
                ["artist_id INTEGER PRIMARY KEY", "artist_uri_id VARCHAR UNQIUE NOT NULL", "artist_name VARCHAR NOT NULL"],
                ["album_id INTEGER PRIMARY KEY", "album_uri_id VARCHAR UNIQUE NOT NULL", "artist_id INTEGER NOT NULL", "album_name VARCHAR NOT NULL", "release_date VARCHAR", "release_type VARCHAR"]]


def create_table(conn, db, table_name, columns):
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join(columns)})")
    conn.commit()

#TABLE OVERVIEW IN db_organization.txt
def initialize_db(conn, db):
    for i in range(len(tables)):
        create_table(conn, db, tables[i], columns_list[i])

def clear_db(conn, bd):
    for table in tables:
        conn.execute(f"DROP TABLE {table}")
        conn.commit()