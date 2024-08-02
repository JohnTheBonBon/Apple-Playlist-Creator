import ast
import random
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

def run_applescript(script):
    """Run an AppleScript command and return the output."""
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True) # Changed 'subprocess.r
    if result.returncode != 0:
        logging.error(f"AppleScript error: {result.stderr.strip()}")
        return ""
    return result.stdout.strip()

def fetch_albums():
    """Fetch all Albums from the Music library."""
    get_albums = '''
    tell application "Music"
        set albumList to {}
        set albumTrackCounts to {}
        repeat with aTrack in every track of library playlist 1
            set albumName to (get album of aTrack as string)
            if albumName is not in albumList then
                set end of albumList to albumName
            end if
        end repeat
        return albumList
    end tell
    '''
    result = run_applescript(get_albums)

    formatted_albums = "\n" + result.replace(", ", "\n")
    logging.info(f"Albums found... {formatted_albums}")
    if not result:
        logging.info("No albums found in the your library.")
        return []

if __name__ == '__main__':
    fetch_albums()