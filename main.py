import json
import os
import csv

from Functions.file_management import *
from Functions.data_management import *
from Functions.custom_metrics import *


#CORE FUNCTIONS

#Get constants from a file 
def get_constants():
    constants = {}

    with open("constants.txt", "r") as f:
        text = f.readlines()

    for line in text:
        field, value = line.split("=")
        constants[field] = value[:-1]

    return constants

#Renames Marquee into Artists
#Get the data from the files (currently combining: streamed_music)
def extract_data(folder_name, playlistFile, stream_file_names, silent=False):
    files = [i for i in os.listdir(folder_name) if i[-5:] == ".json"]
    data = {}
    typeInfo = {}

    for file in files:
        with open("./"+folder_name+"/"+file, "r", encoding="utf8") as f:
            if not silent:
                print(f"Processing {file}.")
            
            text = f.read()
            
            try:
                jsonText = json.loads(text)
            except:
                jsonText = "[JSON_FAILED]"+text
            
            if isinstance(jsonText, list):
                type_char = 'l'
            elif isinstance(jsonText, dict):
                type_char = 'd'
            elif isinstance(jsonText, str):
                type_char = 's'
            else:
                type_char = 'u'

            typeInfo[file[:-5]] = type_char
            data[file[:-5]] = jsonText
    
    for file_name in stream_file_names:
        combine_streaming_history(data, typeInfo, file_name)
    
    try:
        data["Artists"] = data["Marquee"]
        typeInfo["Artists"] = typeInfo["Marquee"]

        del data["Marquee"]
        del typeInfo["Marquee"]
    except:
        pass

    try:
        data["Playlists"] = data[playlistFile]
        typeInfo["Playlists"] = typeInfo[playlistFile]

        del data[playlistFile]
        del typeInfo[playlistFile]
    except:
        pass

    return data, typeInfo

#Format the data structures correctly (currently formatting: playlists, artists, streamed_music)
def raw_data_handling(data, typeInfo, storageFile=None):
    clean_playlists(data, 'Playlists')
    adjust_artists(data, typeInfo, "Artists")
    clean_streaming_audio(data, "Streaming_History_Audio")

#TODO: Analyze Data (might delete and just create funcctions in custom_metrics to be called in main)
def analysis(data, typeInfo, file=None):
    pass



def main():
    #Get Constants from a file
    constants = get_constants()

    #Different constants
    streamFiles = [constants["Stream_History_Music"], constants["Stream_History_Video"]]
    spotifyDataFolder = constants["Spotify_Data_Folder"]
    pfile = constants['Playlists']

    #Extract data from zip
    get_data_from_zip(constants)

    #Got data into two dictionaries with the data and data structure type (typeInfo might be useless, but i left it incase future needs)
    data, typeInfo = extract_data(spotifyDataFolder, pfile, streamFiles, silent=True)
    #Fixed raw json data into better data structures
    raw_data_handling(data, typeInfo)

    #Begin Testing (used to seperate standard code from testing)

    #Got the raw song, artist, album rankings and total amount of timme listened all in ms
    raw_songs, total = get_all_time_song_info(data, constants["Stream_History_Music"])
    raw_artists = get_all_time_artist_info(data, constants["Stream_History_Music"])
    raw_albums = get_all_time_album_info(data, constants["Stream_History_Music"])

    #Converting everything into minutes (songs, artists, albums)
    songs = [(i[0], round(i[1]/60)/1000.0, i[2]) for i in raw_songs]
    artists = [(i, round(j/60)/1000.0) for i, j in raw_artists]
    albums = [(i[0], round(i[1]/60)/1000.0, i[2]) for i in raw_albums]

    #End Testing

if __name__ == "__main__":
    main()
