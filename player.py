import ansiescapes as ae
from moviepy import VideoFileClip
from PIL import Image
import sys, time, os, threading


video_status_lock = threading.Lock()
terminated = False


def test_terminal():
    try:
        os.get_terminal_size()
    except Exception:
        print('You should run this in a terminal. It runs like this:')
        print('python player.py <VIDEO_PATH>')
        return False
    return True

# find the nearest color classification with RGB (-> HSV)
def choose_low_color(rgb):
    r, g, b = rgb
    min_v = min(r, g, b)
    max_v = max(r, g, b)

    # calculate saturation [0, 1)
    if max_v == 0:
        s = 0
    else:
        s = 1 - min_v / max_v

    # calculate value [0, 1)
    v = max_v / 255

    # calculate hue [0, 360)
    h = 0
    if max_v == min_v:
        h = 0
    elif max_v == r and g >= b:
        h = 60 * (g - b) / (max_v - min_v)
    elif max_v == r and g < b:
        h = 60 * (g - b) / (max_v - min_v) + 360
    elif max_v == g:
        h = 60 * (b - r) / (max_v - min_v) + 120
    elif max_v == b:
        h = 60 * (r - g) / (max_v - min_v) + 240

    # classification
    if s < 0.15 or v < 0.1:
        return 'gray'
    if h >= 330 or h < 30:
        return 'red'
    elif 30 <= h < 90:
        return 'anti_blue'
    elif 90 <= h < 150:
        return 'green'
    elif 150 <= h < 210:
        return 'anti_red'
    elif 210 <= h < 270:
        return 'blue'
    elif 270 <= h < 330:
        return 'anti_green'
    else:
        return 'gray'


def choose_char(rgb):
    r, g, b = rgb
    depth = r * 0.299 + g * 0.587 + b * 0.114
    depth = 10 - int(depth / 255 * 10)
    return '#@%|^*=:-. '[depth]


def print_image(img, size, enable_color):
    total = []
    last_low_color = '_'
    sys.stdout.write(ae.cursor_to(0, 0))
    if not enable_color:
        sys.stdout.write(ae.set_low_color('gray'))
    for j in range(size[1]):
        line = ''
        for i in range(size[0]):
            pixel = img.getpixel(xy=(int(i/size[0]*img.size[0]), int(j/size[1] * img.size[1])))
            low_color = choose_low_color(pixel)
            line += (ae.set_low_color(low_color)
                     if low_color != last_low_color  # lazy update color
                        and enable_color
                     else '') + choose_char(pixel)
            last_low_color = low_color
        total.append(line)

    sys.stdout.write('\n'.join(total))


def print_bar(col, length, playing, progress):
    state = ' > ' if not playing else ' = '
    cnt = int(progress * (length - 3))
    sys.stdout.write(ae.set_low_color('gray'))
    sys.stdout.write(ae.cursor_to(0, col) + state + '#' * (1 + cnt) + '-' * max(0, length - 4 - cnt))


def key_sprite(video_status):
    global terminated
    getchar = None
    if os.name == 'nt':
        import msvcrt
        getchar = msvcrt.getwch

    while True:
        # listen user input
        ch = getchar()
        video_status_lock.acquire()

        if ch == 'q':
            terminated = True
            video_status_lock.release()
            break
        elif ch == 'a':
            video_status['now'] -= 10
        elif ch == 'd':
            video_status['now'] += 10
        elif ch == 'p':
            video_status['playing'] = not video_status['playing']
        elif ch == 'c':
            video_status['enable_color'] = not video_status['enable_color']

        video_status['now'] = max(0, min(video_status['now'], video_status['duration']))
        video_status_lock.release()


def main(file_path):
    global terminated
    clip = VideoFileClip(file_path)
    duration = clip.duration
    sys.stdout.write(ae.clear_screen)
    now = -1
    enable_color = False

    video_status = {
        'playing': True,
        'progress': 0,
        'now': 0,
        'duration': duration,
        'enable_color': enable_color
    }
    threading.Thread(target=key_sprite, args=(video_status,)).start()

    while not terminated:
        # update status
        cmd_size = (os.get_terminal_size().columns, os.get_terminal_size().lines)
        video_status_lock.acquire()
        need_update = now != video_status['now'] or enable_color != video_status['enable_color']
        playing = video_status['playing']
        enable_color = video_status['enable_color']
        now = min(video_status['now'], duration-0.05)
        video_status_lock.release()
        start = time.time()

        # draw frame
        if (need_update or playing):
            arr = clip.get_frame(now)
            img = Image.fromarray(arr)
            print_image(img, (cmd_size[0], cmd_size[1]-1), enable_color)
            print_bar(cmd_size[1]-1, cmd_size[0], playing, now / duration)
            sys.stdout.flush()
        else:
            time.sleep(0.05)

        # calculate cost
        if playing:
            cost = time.time() - start
        else:
            cost = 0

        # update frame
        video_status_lock.acquire()
        if video_status['now'] == now:
            video_status['now'] = now + cost
        video_status['now'] = min(video_status['now'], duration-0.05)
        video_status_lock.release()
        if now + cost >= duration:
            continue


if __name__ == '__main__':
    if test_terminal():
        f = sys.argv[1]
        main(f)

