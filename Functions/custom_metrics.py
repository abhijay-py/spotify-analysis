#Gets values of artistDict or the different levels of listner
def get_listening_types(artistDict):
    types = []
    
    for i in artistDict.values():
        if i not in types:
            types.append(i)

    return types

#Returns list of (SongName, ms_listened, ArtistName, AlbumName, uri) (sorted from least listened to most)
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

#Returns list of (ArtistName, ms_listened) (sorted from least listened to most)
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

#Returns list of (AlbumName, ms_listened, ArtistName) (sorted from least listened to most)
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
