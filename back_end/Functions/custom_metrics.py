from Functions.data_management import song_info_extraction, uri_indexing

#GET DATA INFO

#Gets values of artistDict or the different levels of listner
def get_listening_types(data):
    artistDict = data["Artists"]

    types = []
    
    for i in artistDict.values():
        if i not in types:
            types.append(i)

    return types

#Gets types of stream start and end events 
def get_stream_start_end_types(data, file_name):
    streams = data[file_name]
    start_types = []
    end_types = []

    for stream in streams:
        reason_start = stream["play_info"]["reason_start"] 
        reason_stop = stream["play_info"]["reason_end"]

        if reason_start not in start_types:
            start_types.append(reason_start)
        if reason_stop not in end_types:
            end_types.append(reason_stop)

    return start_types, end_types
    

#METRICS

#Returns list of (SongName, ms_listened, ArtistName, AlbumName, uri, other_uris) (sorted from least listened to most)
def get_all_time_song_info(data, file_name):
    return song_info_extraction(data, file_name)

#Returns list of (ArtistName, ms_listened) (sorted from least listened to most)
def get_all_time_artist_info(data, file_name):
    songs, total = song_info_extraction(data, file_name)
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
    songs, total = song_info_extraction(data, file_name)
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

#Returns Dict with key playlistname and values of (ms_listened, song_ranking, artist_ranking, album_ranking) (Duplicated songs and Local Files will not be included in total)
def get_playlist_info(data, song_file_name):
    playtimeUriIndexing, similarUriIndexing, reverseUriIndexing = uri_indexing(data, song_file_name)
    playlists = {}
       
    for playlistName, info in data['Playlists'].items():
        mainUris = []
        totalTime = 0
        songs = []
        artists = {}
        albums = {}

        for song in info[1]:
            items = list(song.items())
            songName = items[0][0]
            songInfo = items[0][1]
            uri = songInfo['trackUri']
            artist = songInfo['artistName']
            album = songInfo['albumName']

            if uri not in similarUriIndexing.keys():
                if songName+artist in reverseUriIndexing.keys():
                    uri = reverseUriIndexing[songName+artist]
                else:
                    songs.append((songName, 0))
                    if artist not in artists.keys():
                        artists[artist] = 0
                    if album not in albums.keys():
                        albums[album] = 0
                    continue
            if similarUriIndexing[uri] in mainUris:
                continue
            else:
                mainUris.append(similarUriIndexing[uri])

            duration = playtimeUriIndexing[uri]
            totalTime += duration

            songs.append((songName, duration))

            if artist not in artists.keys():
                artists[artist] = duration
            else:
                artists[artist] += duration

            if album not in albums.keys():
                albums[album] = duration
            else:
                albums[album] += duration
        
        finalArtists = [(i, j) for i, j in artists.items()]
        finalAlbums = [(i, j) for i, j in albums.items()]
        
        sortedSongs = sorted(songs, key=lambda x:x[1])
        sortedArtists = sorted(finalArtists, key=lambda x:x[1])
        sortedAlbums = sorted(finalAlbums, key=lambda x:x[1])

        playlists[playlistName] = [totalTime, sortedSongs, sortedArtists, sortedAlbums]

    return playlists
