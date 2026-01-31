import tkintermapview
import os

db_filename = "offline_map.db"

loader = tkintermapview.OfflineLoader(path=db_filename)

top_left_position = (39.743, -4.4461)
bottom_right_position = (38.542, -3.571)

zoom_min = 7
zoom_max = 14

print(f"Starting download to {db_filename}...")

# Run the download
loader.save_offline_tiles(top_left_position,
                          bottom_right_position,
                          zoom_min,
                          zoom_max)

print("Download completed.")
