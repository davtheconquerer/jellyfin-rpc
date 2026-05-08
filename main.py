import json
import time
import requests
from pypresence import Presence

# 1. Load the Configuration
with open("config.json", "r") as f:
    config = json.load(f)

CLIENT_ID = config["client_id"]
SERVER_URL = config["server_url"].rstrip('/')
API_KEY = config["api_key"]
USERNAME = config["username"]

HEADERS = {
    "Authorization": f'MediaBrowser Token="{API_KEY}"',
    "Content-Type": "application/json"
}

def format_time(ticks):
    """Converts Jellyfin ticks to hh:mm:ss format"""
    if not ticks:
        return "00:00:00"
    
    total_seconds = int(ticks / 10000000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_user_id():
    """Fetches the Jellyfin User ID."""
    try:
        response = requests.get(f"{SERVER_URL}/Users", headers=HEADERS)
        response.raise_for_status()
        users = response.json()
        for user in users:
            if user["Name"].lower() == USERNAME.lower():
                return user["Id"]
        print(f"Error: Could not find user '{USERNAME}'")
        return None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def get_playback_info(user_id):
    """Checks what the user is watching and grabs the ticks."""
    try:
        response = requests.get(f"{SERVER_URL}/Sessions", headers=HEADERS)
        response.raise_for_status()
        sessions = response.json()
        
        for session in sessions:
            if session.get("UserId") == user_id and "NowPlayingItem" in session:
                item = session["NowPlayingItem"]
                play_state = session.get("PlayState", {})
                
                info = {
                    "item_id": item.get("Id"), # Added this back to track if the movie changed
                    "title": item.get("Name", "Unknown Title"),
                    "type": item.get("Type", "Unknown"),
                    "is_paused": play_state.get("IsPaused", False),
                    "current_ticks": play_state.get("PositionTicks", 0),
                    "total_ticks": item.get("RunTimeTicks", 0) 
                }
                
                if info["type"] == "Episode":
                    info["series"] = item.get("SeriesName", "Unknown Series")
                
                return info
        return None 
    except Exception as e:
        print(f"API Error: {e}")
        return None

def main():
    print("Starting Jellyfin Discord Rich Presence...")
    
    user_id = get_user_id()
    if not user_id:
        return

    rpc = Presence(CLIENT_ID)
    rpc.connect()
    print("Connected to Discord!")

    # Variables to "anchor" the green timer
    current_item_id = None
    cached_start_epoch = None
    RPC_CLEARED = False

    while True:
        try:
            playback = get_playback_info(user_id)
            
            if playback:
                RPC_CLEARED = False # Reset the cleared flag since we have something to show
                # Format the Text Details
                if playback["type"] == "Episode":
                    details = f"{playback['series']} - {playback['title']}"
                else:
                    details = f"{playback['title']}"

                current_time_str = format_time(playback["current_ticks"])
                total_time_str = format_time(playback["total_ticks"])
                timing_display = f"{current_time_str} / {total_time_str}"

                # Calculate the exact epoch time the media started
                elapsed_seconds = int(playback["current_ticks"] / 10000000)
                calculated_start = int(time.time() - elapsed_seconds)

                # Update the anchor ONLY if we changed movies, OR if you skipped/rewound by more than 5 seconds
                if playback["item_id"] != current_item_id:
                    current_item_id = playback["item_id"]
                    cached_start_epoch = calculated_start
                elif cached_start_epoch and abs(calculated_start - cached_start_epoch) > 5:
                    cached_start_epoch = calculated_start

                # Push Update to Discord
                if playback["is_paused"]:
                    rpc.update(
                        details=details,
                        state=f"Paused [{timing_display}]",
                        large_image="jellyfin_logo",
                        large_text="Jellyfin"
                        # We do NOT send a start time here, so the green timer vanishes while paused
                    )
                    print(f"Paused - {details}")
                else:
                    rpc.update(
                        details=details,
                        state=f"Watching [{timing_display}]", 
                        large_image="jellyfin_logo",
                        large_text="Jellyfin",
                        start=cached_start_epoch # Send the anchored time to keep the green timer steady!
                    )
                    print(f"Watching - {details} [{timing_display}]")
            else:
                if not RPC_CLEARED: # Only clear if we haven't already
                    rpc.clear()
                    RPC_CLEARED = True
                    current_item_id = None # Reset anchor
                    cached_start_epoch = None
                    print("Nothing playing. Cleared RPC.")
                else:
                    print("Nothing playing. RPC already cleared.")

        except Exception as e:
            print(f"Error in loop: {e}")

        # Sleep for 15 seconds
        time.sleep(15)

if __name__ == "__main__":
    main()