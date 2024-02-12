from Functions.custom_metrics import *
import sqlite3 

def create_table(db, table_name, columns):
    conn = sqlite3.connect(db)
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join(columns)})")

def initialize_db(data, typeInfo):
    tables = ["Playlists", "PlaylistTracks", "UserTracks", "UserArtists", "StreamingInfo", "StreamingPlatform", "StreamingEpisode", "Tracks", "Artists", "Albums"]