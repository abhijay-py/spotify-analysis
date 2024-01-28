import json
import os
from urllib.parse import unquote
from github_helper import *

#Helpers
#TEMPORARY (WILL UPDATE WHEN FULL STREAMING DATA IS OUT)
def combine_streaming_history(data, typeInfo, file_name):
    files = [i for i in data.keys() if i.startswith(file_name)]
    streamingInfo = []
    typeSpecificInfo = typeInfo[files[0]]

    for file in files:
        streamingInfo.extend(data[file])
        del data[file]
        del typeInfo[file]

    data[file_name] = streamingInfo
    typeInfo[file_name] = typeSpecificInfo

def convert_local_file(song):
    htmlcode = song["localTrack"]["uri"]
    codedData = htmlcode[14:]
    info = [htmlcode]

    savedText = ""
    for c in codedData:
        if c == ':':
            info.append(unquote(savedText).replace("+", " "))
            savedText = ""
        else:
            savedText += c
        
        if len(info) == 4:
            break
    return {"trackName":info[3], "artistName":info[1], "albumName":info[2], "trackUri":info[0]}
    
def clean_playlists(data, file_name):
    playlistList = data[file_name]["playlists"]
    playlistDict = {}
    for i in playlistList:
        name = i['name']
        date = i['lastModifiedDate']
        items = i['items']
        newItems = []
        
        for song in items:
            trackDict = {}
            track = song["track"]

            if track is None:
                track = convert_local_file(song)

            addedDate = song["addedDate"] #convert into datetime object??? IDK
            trackDict[track["trackName"]] = {"artistName":track["artistName"], "albumName":track["albumName"], "trackUri":track["trackUri"], "episode":song["episode"], "localTrack":song["localTrack"], "addedDate":addedDate}
            newItems.append(trackDict)

        playlistDict[name] = (date, newItems)

    data[file_name] = playlistDict
    


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

#Get the data from the files (currently combining: streamed_music)
def extract_data(folder_name, stream_file_names, silent=False):
    files = [i for i in os.listdir(folder_name) if i[-5:] == ".json"]
    data = {}
    typeInfo = {}

    for file in files:
        with open(".\\"+folder_name+"\\"+file, "r", encoding="utf8") as f:
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

    return data, typeInfo

#Format the data structures correctly (currently formatting: playlists)
def raw_data_handling(data, typeInfo, constants):
    clean_playlists(data, constants['Playlists'])

#Analyze Data
def analysis(data, typeInfo):
    pass



def main():
    constants = get_constants()

    streamFiles = [constants["Stream_History_Music"]]
    spotifyDataFolder = constants["Spotify_Data_Folder"]
    pfile = constants['Playlists']

    data, typeInfo = extract_data(spotifyDataFolder, streamFiles, silent=True)
    raw_data_handling(data, typeInfo, constants)

    #Begin Testing
    playlists = data[pfile]
    for k, v in playlists.items():
        print(f"Playlist: {k}, Songs: {len(v[1])}")

    for i in playlists["Vibes"][1]:
        print(list(i.keys())[0])

    #End Testing

    

    update_gitignore(spotifyDataFolder)


if __name__ == "__main__":
    main()
