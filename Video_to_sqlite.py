import os
import shutil
import sqlite3
import subprocess

video_path = "greatapple.mp4"
db_output_path = "greatapple.db"
WIDTH, HEIGHT = 64, 24
frame_size = WIDTH * HEIGHT
ASCII_CHARS = " .:-=+*#%@"
scale_factor = (len(ASCII_CHARS) - 1) / 255.0

ffmpeg_bin = shutil.which("ffmpeg") or ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW") else 0

conn = sqlite3.connect(db_output_path)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS bad_apple;")
cursor.execute("CREATE TABLE bad_apple (frame_id INTEGER PRIMARY KEY, frame_data TEXT);")

cmd = [ffmpeg_bin, "-i", video_path, "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{WIDTH}x{HEIGHT}", "-"]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)

def frame_generator():
    fid = 0
    read_exact = process.stdout.read
    while True:
        raw = read_exact(frame_size)
        if not raw or len(raw) < frame_size:
            break
        lines = [
            "".join(ASCII_CHARS[int(p * scale_factor)] for p in raw[r * WIDTH : (r + 1) * WIDTH])
            for r in range(HEIGHT)
        ]
        yield (fid, "\n".join(lines))
        fid += 1

cursor.executemany("INSERT INTO bad_apple (frame_id, frame_data) VALUES (?, ?)", frame_generator())
conn.commit()
conn.close()
process.wait()
print("Done!")
