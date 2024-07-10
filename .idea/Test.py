import ast
import random
import subprocess

def get_all_genres():
    get_genres = '''
    tell application "Music"
        set allTracks to every track of library playlist 1
        set genreList to ""
        repeat with aTrack in allTracks
            set theGenre to genre of aTrack
            if theGenre is not "" and theGenre is not in genreList then
                set genreList to genreList & theGenre & ", "
            end if
        end repeat
        return text 1 thru -3 of genreList
    end tell
    '''
    result = subprocess.run(['osascript', '-e', get_genres], capture_output=True, text=True)
    return result.stdout.split(', ')

def add_genre_to_playlist(playlist_name, genre, track_limit):
    # Fetch tracks of the specified genre
    get_tracks = f'''
    tell application "Music"
        set genreTracks to every track of library playlist 1 whose genre contains "{genre}"
        set trackList to ""
        repeat with aTrack in genreTracks
            set trackList to trackList & "(" & (get database ID of aTrack as string) & ", " & (get duration of aTrack as string) & ", \\"" & (get album of aTrack as string) & "\\", \\"" & (get artist of aTrack as string) & "\\")" & ", "
        end repeat
        return "[" & text 1 thru -3 of trackList & "]"
    end tell
    '''

    result = subprocess.run(['osascript', '-e', get_tracks], capture_output=True, text=True)
    if result.stdout.strip() == "":
        print(f"No tracks found in {genre} genre.")
        return
    track_tuples = ast.literal_eval(result.stdout)
    tracks = [{'id': int(id), 'duration': float(duration), 'album': album, 'artist': artist} for id, duration, album, artist in track_tuples]

    # Shuffle tracks here before any checks
    random.shuffle(tracks)

    if len(tracks) < 5:
        print(f"Not enough tracks in {genre} genre to create a playlist.")
        return

    # Group tracks by album to check for diversity
    albums = {}
    for track in tracks:
        if track['album'] in albums:
            albums[track['album']].append(track)
        else:
            albums[track['album']] = [track]

    if len(albums) <= 2:
        print(f"Not enough album diversity in {genre} genre, but playlist will still be created with shuffled tracks.")
        # Even if not enough album diversity, proceed with playlist creation since tracks are already shuffled

    # Proceed to create or clear the playlist
    get_or_create_playlist = f'''
    tell application "Music"
        if exists (some playlist whose name is "{playlist_name}") then
            set existingPlaylist to some playlist whose name is "{playlist_name}"
            delete every track of existingPlaylist
        else
            set existingPlaylist to (make new playlist with properties {{name:"{playlist_name}"}})
        end if
    end tell
    '''
    subprocess.run(['osascript', '-e', get_or_create_playlist])

    # Add tracks to the playlist
    added_tracks = 0
    last_added_album = None

    last_artist = None
    consecutive_count = 0
    album_count = len(albums)

    for track in tracks:
        if added_tracks >= track_limit:
            break

        current_artist = track['artist']
        # Check if current artist is the same as the last artist
        if current_artist == last_artist:
            consecutive_count += 1
        else:
            consecutive_count = 1  # Reset count for a new artist

        last_artist = current_artist  # Update the last artist

        # Skip adding the track if the artist has appeared more than twice consecutively
        if consecutive_count > 2:
            continue

        # Check if current track album is different from previous
        if track['album'] != last_added_album or album_count <= 2:
            add_track_to_playlist = f'''
            tell application "Music"
                set theTrack to some track of library playlist 1 whose database ID is {track['id']}
                duplicate theTrack to some playlist whose name is "{playlist_name}"
            end tell
            '''
            subprocess.run(['osascript', '-e', add_track_to_playlist])
            added_tracks += 1
            last_added_album = track['album']

genres = get_all_genres()
genres = [genre.strip() for genre in genres]
print(genres)

for genre in genres:
    playlist_name = f"{genre} Mix"
    track_count = 15
    add_genre_to_playlist(playlist_name, genre, track_count)