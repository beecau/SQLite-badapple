import sqlite3
import subprocess


video_path = "greatapple.mp4"
db_output_path = "greatapple.db"


WIDTH = 64
HEIGHT = 24
frame_size = WIDTH * HEIGHT
ASCII_CHARS = " .:-=+*#%@"


# Initialize SQLite database

conn = sqlite3.connect(db_output_path)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS bad_apple;")
cursor.execute("CREATE TABLE bad_apple (frame_id INTEGER PRIMARY KEY, frame_data TEXT);")


# FFmpeg command to output raw grayscale frames directly to stdout

cmd = [
    "ffmpeg",
    "-i",
    video_path,
    "-f",
    "rawvideo",
    "-pix_fmt",
    "gray",
    "-s",
    f"{WIDTH}x{HEIGHT}",
    "-",
]


print("Processing video frames with FFmpeg...")
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

frame_id = 0

while True:
  raw_frame = process.stdout.read(frame_size)
  if not raw_frame or len(raw_frame) < frame_size:
    break

  lines = []
  for r in range(HEIGHT):
    row_bytes = raw_frame[r * WIDTH : (r + 1) * WIDTH]
    line = "".join(
        ASCII_CHARS[int(pixel / 255 * (len(ASCII_CHARS) - 1))]
        for pixel in row_bytes

    )

    lines.append(line)
  ascii_art = "\n".join(lines)

  cursor.execute(
      "INSERT INTO bad_apple (frame_id, frame_data) VALUES (?, ?)",
      (frame_id, ascii_art),

  )

  frame_id += 1

conn.commit()
conn.close()
process.wait()
print(f"Done! Generated {frame_id} frames into SQLite database: {db_output_path}") 
