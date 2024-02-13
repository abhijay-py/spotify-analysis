from Functions.spotify_api import *
import sqlite3 

tables = ["users", "playlists",  "user_tracks", "user_artists", "streaming_info"]
columns_list = [["user_id INTEGER PRIMARY KEY", "username VARCHAR UNIQUE NOT NULL"],
                ["playlist_id INTEGER PRIMARY KEY", "playlist_uri_id VARCHAR UNQIUE NOT NULL", "track_id INTEGER NOT NULL", "user_id INTEGER NOT NULL"],
                ["user_id INTEGER PRIMARY KEY", "track_id INTEGER UNIQUE NOT NULL", "ms_listened INTEGER NOT NULL"],
                ["user_id INTEGER PRIMARY KEY", "artist_id INTEGER UNIQUE NOT NULL", "listening_type VARCHAR NOT NULL"],
                ["stream_id INTEGER PRIMARY KEY", "user_id INTEGER NOT NULL", "track_uri_id VARCHAR NOT NULL", "timestamp VARCHAR NOT NULL", "ms_played INTEGER NOT NULL", "reason_start VARCHAR", "reason_end VARCHAR", "shuffle VARCHAR", 
                    "skipped VARCHAR", "platform VARCHAR", "country VARCHAR", "client VARCHAR", "offline VARCHAR", "offline_timestamp VARCHAR", "incognito_mode VARCHAR", "episode_name VARCHAR", "episode_show VARCHAR", "episode_uri VARCHAR"]]

#Helper Function
def check_exists(curr, sql):
    curr.execute(sql)
    info = curr.fetchall()

    return len(info) != 0

def create_table(conn, table_name, columns):
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join(columns)})")
    conn.commit()

#Core DB Functions
def initialize_db(conn):
    for i in range(len(tables)):
        create_table(conn, tables[i], columns_list[i])

def clear_db(conn):
    for table in tables:
        try:
            conn.execute(f"DROP TABLE {table}")
            conn.commit()
        except:
            pass

#VERY INEFFICIENT, (might just calculate stats and save that instead)
def add_streams(conn, data, file_name):
    streams = data[file_name]
    curr = conn.cursor()
    username_to_id = {}

    add_stream_sql = '''INSERT INTO streaming_info(user_id, track_uri_id, timestamp, ms_played, reason_start, reason_end, shuffle, skipped, platform, country, client, offline, 
                                                    offline_timestamp, incognito_mode, episode_name, episode_show, episode_uri) 
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''

    for stream in streams:
        coreData = stream["main_data"]
        streamData = stream["streaming_info"]
        episodeData = stream["episode_details"]
        playData = stream["play_info"]

        username = streamData['username']
        try:
            trackUriId = coreData['trackUri'].split(":")[-1]
        except:
            continue

        if username not in username_to_id.keys():
            sqlGetUsers = f"SELECT * FROM users WHERE username='{username}'"

            if not check_exists(curr, sqlGetUsers):
                sql = 'INSERT INTO users(username) VALUES(?);'
                curr.execute(sql, (username,))
                conn.commit()

            curr.execute(sqlGetUsers)
            user_id = curr.fetchall()[0][0]

            username_to_id[username] = user_id

            curr.execute(f"DELETE FROM streaming_info WHERE user_id={user_id}")
            conn.commit()
        else:
            user_id = username_to_id[username]
    
        curr.execute(add_stream_sql, (user_id, trackUriId, streamData['timestamp'], playData['ms_played'], playData['reason_start'], playData['reason_end'], 
                            playData['shuffle'], playData['skipped'], streamData['platform'], streamData['country'], streamData['client'],
                            streamData['offline'], streamData['offline_timestamp'], streamData['incognito_mode'], episodeData['episode_name'],
                            episodeData['episode_show'], episodeData['episodeUri']))
        conn.commit()
