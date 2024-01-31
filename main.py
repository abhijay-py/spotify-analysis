import json
import os
import csv
from urllib.parse import unquote
from github_helper import *

#BASIC HELPERS
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

def save_to_csv(info, typeChar, output_file, reverse=False):
    if typeChar == 'll':
        with open(".\\Spotify_Analysis_Files\\"+output_file+".csv", 'w', newline='', encoding="utf-8-sig") as f:
            csv_f = csv.writer(f)
            if not reverse:
                csv_f.writerows()
            else:
                for i in range(len(info) - 1, -1, -1):
                    csv_f.writerow(info[i])


#ADVANCED HELPERS   

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
    
def adjust_artists(data, typeInfo, file_name):
    typeInfo[file_name] = 'd'
    artistDict = {}

    for artist in data[file_name]:
        artistDict[artist["artistName"]] = artist["segment"]

    data[file_name] = artistDict

def clean_streaming_audio(data, file_name):
    songs = data[file_name]
    newSongs = []

    for song in songs:
        newSong = {}

        try:
            client = unquote(song['user_agent_decrypted'])
        except:
            client = None
        
        if song['ms_played'] == 0:
            continue

        coreData = {'trackName':song['master_metadata_track_name'], 'artistName':song['master_metadata_album_artist_name'], 'albumName':song['master_metadata_album_album_name'], 'trackUri':song['spotify_track_uri']}
        streamData = {'timestamp':song['ts'], 'platform':song['platform'], 'country':song['conn_country'], 'ip':song['ip_addr_decrypted'], 'client':client, 
                        'offline':song['offline'], 'offline_timestamp':song['offline_timestamp'], 'incognito_mode':song['incognito_mode']}
        episodeData = {'episode_name':song['episode_name'], 'episode_show':song['episode_show_name'], 'episodeUri':song['spotify_episode_uri']}
        playData = {'ms_played':song['ms_played'], 'reason_start':song['reason_start'], 'reason_end':song['reason_end'], 'shuffle':song['shuffle'], 'skipped':song['skipped']}

        newSong["main_data"] = coreData
        newSong["streaming_info"] = streamData
        newSong["episode_details"] = episodeData
        newSong["play_info"] = playData

        newSongs.append(newSong)

    data[file_name] = newSongs


#NON CORE FUNCTIONS

def get_listening_types(artistDict):
    types = []
    
    for i in artistDict.values():
        if i not in types:
            types.append(i)

    return types

def get_all_time_song_info(data, file_name):
    total = 0
    uriTracker = {}
    reversereference = {}
    realreference = {}

    for song in data['Streaming_History_Audio']:
        core_data = song['main_data']
        play_info = song['play_info']

        uri = core_data['trackUri']
        name = core_data['trackName']
        artist = core_data['artistName']
        album = core_data['albumName']
        ms_played = play_info['ms_played']

        if song['episode_details']['episode_name']:
            continue

        total += ms_played

        if name == None or artist == None:
            continue
        
        if name + artist in reversereference.keys():
            uri = reversereference[name+artist]
        else:
            realreference[uri] = (name, artist, album)
            reversereference[name+artist] = uri

        
        if uri not in uriTracker.keys():
            uriTracker[uri] = ms_played
        else:
            uriTracker[uri] += ms_played

    sortedStuff = sorted(uriTracker.items(), key=lambda x:x[1])
    sortedBetter = [(realreference[i][0], j, realreference[i][1], realreference[i][2], i) for i, j in sortedStuff]
    
    return sortedBetter, total

def get_all_time_artist_info(data, file_name):
    songs, total = get_all_time_song_info(data, file_name)
    artists = {}

    for song in songs:
        artist = song[2]
        ms_listened = song[1]

        if artist in artists.keys():
            artists[artist] += ms_listened
        else:
            artists[artist] = ms_listened

    sortedStuff = sorted(artists.items(), key=lambda x:x[1])

    return sortedStuff

def get_all_time_album_info(data, file_name):
    songs, total = get_all_time_song_info(data, file_name)
    albums = {}
    albumToArtist = {}

    for song in songs:
        album = song[3]
        artist = song[2]
        ms_listened = song[1]

        albumToArtist[album] = artist

        if album in albums.keys():
            albums[album] += ms_listened
        else:
            albums[album] = ms_listened

    sortedStuff = sorted(albums.items(), key=lambda x:x[1])
    sortedBetter = [(i, j, albumToArtist[i]) for i, j in sortedStuff]

    return sortedBetter

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

#Format the data structures correctly (currently formatting: playlists)
def raw_data_handling(data, typeInfo, storageFile=None):
    clean_playlists(data, 'Playlists')
    adjust_artists(data, typeInfo, "Artists")
    clean_streaming_audio(data, "Streaming_History_Audio")

#Analyze Data
def analysis(data, typeInfo, file=None):
    pass



def main():
    constants = get_constants()

    streamFiles = [constants["Stream_History_Music"], constants["Stream_History_Video"]]
    spotifyDataFolder = constants["Spotify_Data_Folder"]
    pfile = constants['Playlists']

    data, typeInfo = extract_data(spotifyDataFolder, pfile, streamFiles, silent=True)
    raw_data_handling(data, typeInfo)

    raw_songs, total = get_all_time_song_info(data, constants["Stream_History_Music"])
    raw_artists = get_all_time_artist_info(data, constants["Stream_History_Music"])
    raw_albums = get_all_time_album_info(data, constants["Stream_History_Music"])

    songs = [(i[0], round(i[1]/60)/1000.0, i[2]) for i in raw_songs]
    artists = [(i, round(j/60)/1000.0) for i, j in raw_artists]
    albums = [(i[0], round(i[1]/60)/1000.0, i[2]) for i in raw_albums]

    #Begin Testing
    save_to_csv(songs, 'll', 'songs', reverse=True)
    save_to_csv(artists, 'll', 'artists', reverse=True)
    save_to_csv(albums, 'll', 'albums', reverse=True)
    #End Testing

    update_gitignore(spotifyDataFolder)


if __name__ == "__main__":
    main()
