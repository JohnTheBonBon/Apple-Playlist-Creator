import ast
import random
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

def run_applescript(script):
    """Run an AppleScript command and return the output."""
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"AppleScript error: {result.stderr.strip()}")
        return ""
    return result.stdout.strip()

def fetch_recently_added_tracks():
    """Fetch all tracks from the 'Recently Added CONFIG' playlist."""
    get_tracks = '''
    tell application "Music"
        set configPlaylist to some playlist whose name is "Recently Added CONFIG"
        set trackList to ""
        repeat with aTrack in every track of configPlaylist
            set trackList to trackList & "(" & (get database ID of aTrack as string) & ", \\"" & (get album of aTrack as string) & "\\")" & ", "
        end repeat
        return "[" & text 1 thru -3 of trackList & "]"
    end tell
    '''
    result = run_applescript(get_tracks)
    logging.info(f"AppleScript result: {result}")
    if not result:
        logging.info("No tracks found in the 'Recently Added CONFIG' playlist.")
        return []

    try:
        track_tuples = ast.literal_eval(result)
    except Exception as e:
        logging.error(f"Error parsing AppleScript result: {e}")
        return []

    return [{'id': int(id), 'album': album} for id, album in track_tuples]

def create_or_clear_playlist():
    """Create a new playlist or clear an existing one."""
    clear_playlist = f'''
    tell application "Music"
        if exists (some playlist whose name is "Recently Added") then
            set existingPlaylist to some playlist whose name is "Recently Added"
            delete every track of existingPlaylist
        else
            set existingPlaylist to (make new playlist with properties {{name:"Recently Added"}})
        end if
    end tell
    '''
    run_applescript(clear_playlist)

def add_track_to_playlist(track_id):
    """Add a track to the specified playlist by database ID."""
    add_track = f'''
    tell application "Music"
        set theTrack to some track of library playlist 1 whose database ID is {track_id}
        duplicate theTrack to some playlist whose name is "Recently Added"
    end tell
    '''
    run_applescript(add_track)

def remove_track_from_playlist(track_id):
    """Remove a track from the 'Recently Added' playlist by database ID."""
    remove_track = f'''
    tell application "Music"
        set recentPlaylist to some playlist whose name is "Recently Added"
        delete (every track of recentPlaylist whose database ID is {track_id})
    end tell
    '''
    run_applescript(remove_track)

def edit_recently_added_playlist():
    """Edit the 'Recently Added' playlist to ensure no album appears more than three times."""
    config_tracks = fetch_recently_added_tracks()
    if not config_tracks:
        return
    create_or_clear_playlist()

    album_tracks = {}
    """Adds tracks to the 'Recently Added' playlist and counts the number of tracks per album."""
    for track in config_tracks:
        add_track_to_playlist(track['id'])
        album = track['album']
        if album not in album_tracks:
            album_tracks[album] = []
        album_tracks[album].append(track)

    to_remove_tracks = []
    """Removes tracks from the 'Recently Added' playlist if the album appears more than 3 times."""
    for album, tracks, in album_tracks.items():
        if len(tracks) > 3:
            # Randomly select 3 tracks to keep
            tracks_to_keep = random.sample(tracks, 3)
            tracks_to_remove = [track for track in tracks if track not in tracks_to_keep]
            to_remove_tracks.extend(tracks_to_remove)

    for track in to_remove_tracks:
        remove_track_from_playlist(track['id'])

    logging.info(f"Edited playlist 'Recently Added' with {len(to_remove_tracks)} tracks removed.")

if __name__ == '__main__':
    edit_recently_added_playlist()