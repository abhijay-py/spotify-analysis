from urllib.parse import unquote

#Converts any local files in playlists to a more standard format
def convert_local_file(song):
    try:
        htmlcode = song["localTrack"]["uri"]
    except:
        return None
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
                        'offline':song['offline'], 'offline_timestamp':song['offline_timestamp'], 'incognito_mode':song['incognito_mode'], 'username':song['username']}
        episodeData = {'episode_name':song['episode_name'], 'episode_show':song['episode_show_name'], 'episodeUri':song['spotify_episode_uri']}
        playData = {'ms_played':song['ms_played'], 'reason_start':song['reason_start'], 'reason_end':song['reason_end'], 'shuffle':song['shuffle'], 'skipped':song['skipped']}

        newSong["main_data"] = coreData
        newSong["streaming_info"] = streamData
        newSong["episode_details"] = episodeData
        newSong["play_info"] = playData

        newSongs.append(newSong)

    data[file_name] = newSongs

#Gets the streaming data into a better format for metrics. For each song, return (Name, Listening Time, Artist, Album, Primary Uri, Related Uris)
def song_info_extraction(data, file_name):
    total = 0
    uriTracker = {}
    reversereference = {}
    realreference = {}
    otherUris = {}
    count = 0

    for song in data[file_name]:
        count += 1
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
            if uri not in otherUris[reversereference[name+artist]]:
                otherUris[reversereference[name+artist]].append(uri)
            uri = reversereference[name+artist]
        else:
            otherUris[uri] = []
            realreference[uri] = (name, artist, album)
            reversereference[name+artist] = uri

        
        if uri not in uriTracker.keys():
            uriTracker[uri] = ms_played
        else:
            uriTracker[uri] += ms_played

    sortedStuff = sorted(uriTracker.items(), key=lambda x:x[1])
    sortedBetter = [(realreference[i][0], j, realreference[i][1], realreference[i][2], i, otherUris[i]) for i, j in sortedStuff]
    
    return sortedBetter, total

#Returns two dictionaries associating uris with the primary uri and the songs playtime. Also returns a reverse reference dict for name+artist to mainuri.
def uri_indexing(data, song_file_name):
    songs, total = song_info_extraction(data, song_file_name)
    playtimeUriIndexing = {}
    similarUriIndexing = {}
    reverseUriIndexing = {}

    for song in songs:
        mainUri = song[4]
        otherUris = song[5]
        playtime = song[1]
        name = song[0]
        artist = song[2]

        playtimeUriIndexing[mainUri] = playtime
        similarUriIndexing[mainUri] = mainUri
        reverseUriIndexing[name+artist] = mainUri

        for uri in otherUris:
            playtimeUriIndexing[uri] = playtime
            similarUriIndexing[uri] = mainUri
            
    return playtimeUriIndexing, similarUriIndexing, reverseUriIndexing