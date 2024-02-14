from urllib.parse import unquote

#Converts any local files in playlists to a more standard format
def convert_local_file(song):
    try:
        htmlcode = song["localTrack"]["uri"]
    except:
        return None
    codedData = htmlcode[14:]
    info = [htmlcode]

#Combines all audio streaming history into one data structure
def combine_streaming_history(data, typeInfo, file_name):
    files = [i for i in data.keys() if i.startswith(file_name)]
    if len(files) == 0:
        return False
    streamingInfo = []
    typeSpecificInfo = typeInfo[files[0]]

    for file in files:
        streamingInfo.extend(data[file])
        del data[file]
        del typeInfo[file]
    data[file_name] = streamingInfo
    typeInfo[file_name] = typeSpecificInfo

    return True

#Considering converting datetime into datetime object.
#Rearranges playlist data into an easier format. 
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
                if track is None:
                    continue

            addedDate = song["addedDate"] 
            trackDict[track["trackName"]] = {"artistName":track["artistName"], "albumName":track["albumName"], "trackUri":track["trackUri"], "episode":song["episode"], "localTrack":song["localTrack"], "addedDate":addedDate}
            newItems.append(trackDict)
        playlistDict[name] = (date, newItems)
    data[file_name] = playlistDict
#Rearranges artist (Marquee) data into an easier format   
def adjust_artists(data, typeInfo, file_name):
    typeInfo[file_name] = 'd'
    artistDict = {}
    for artist in data[file_name]:
        artistDict[artist["artistName"]] = artist["segment"]
    data[file_name] = artistDict
#Considering converting datetime into datetime object.
#Rearraanges song data into an easier format
def clean_streaming_audio(data, file_name):
    songs = data[file_name]