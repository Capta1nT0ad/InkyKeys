import subprocess
import time
import select
from PIL import Image, ImageDraw

def capture_touch(timeout=1.0, width=800, height=600, cmd='./read'):
    # start subprocess
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)

    # create image and drawer
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # scale normalized point to image coords
    def scale(p):
        return int(p[0] * width), int((1 - p[1]) * height)

    segments = []
    segment = []
    last_time = None
    stdout_fd = proc.stdout.fileno()

    # read lines with timeout
    while True:
        ready, _, _ = select.select([stdout_fd], [], [], 0.1)
        now = time.time()

        if ready:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()

            # segment separator
            if line == "pass":
                if segment:
                    segments.append(segment)
                    segment = []
                last_time = now

            # parse point lines
            elif line and (line[0] in ('0', '1')):
                try:
                    x, y = map(float, line.split(","))
                    segment.append((x, y))
                    last_time = now
                except ValueError:
                    pass

        # timeout after inactivity
        elif last_time is not None and now - last_time > timeout:
            break

    if segment:
        segments.append(segment)

    # terminate subprocess
    proc.terminate()
    proc.wait()

    # draw all segments on image
    for s in segments:
        if len(s) == 1:
            x, y = scale(s[0])
            draw.ellipse((x-5, y-5, x+5, y+5), fill="black")
        else:
            draw.line([scale(p) for p in s], fill="black", width=3)

    return img


if __name__ == "__main__":
    while True:
        img = capture_touch(timeout=1.5)
        img.save("out.png")
        print("Saved to out.png")
        input()
