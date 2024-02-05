from Functions.data_management import song_info_extraction, uri_indexing

#Gets values of artistDict or the different levels of listner
def get_listening_types(artistDict):
    types = []
    
    for i in artistDict.values():
        if i not in types:
            types.append(i)

    return types

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

#TODO: Erroring on LIFE AFTER SALEM (says played 0). Either uri was never listened to by user or some programming error occured. Report any similar issues. Erroring generally overall (says a song is played more than the most played song)
#Returns list of (PlaylistName, ms_listened, song_ranking, artist_ranking, album_ranking) (sorted from least listened to most) (Duplicated songs and Local Files will not be included in total)
def get_playlist_info(data, song_file_name):
    playtimeUriIndexing, similarUriIndexing = uri_indexing(data, song_file_name)
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

            if songName == 'LIFE AFTER SALEM':
                print(uri)

            if uri not in similarUriIndexing.keys():
                songs.append((songName, 0))
                if artist not in artists.keys():
                    artists[artist] = 0
                if album not in albums.keys():
                    albums[album] = 0
                continue
            if uri in mainUris:
                continue

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
