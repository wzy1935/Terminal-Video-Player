"""
Original file is from ansiescapes.
Github repo: https://github.com/kodie/ansiescapes


MIT License

Copyright (c) 2017 Kodie Grantham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

ESC = '\u001B['
is_terminal_app = True


def cursor_to(x, y=None):
    return ESC + str(y + 1) + ';' + str(x + 1) + 'H'


def cursor_move(x, y=None):
    ret = ''

    if x < 0:
        ret += ESC + '-' + str(x) + 'D'
    elif x > 0:
        ret += ESC + str(x) + 'C'

    if y < 0:
        ret += ESC + '-' + str(y) + 'A'
    elif y > 0:
        ret += ESC + str(y) + 'B'

    return ret


def cursor_up(count=1):
    return ESC + str(count) + 'A'


def cursor_down(count=1):
    return ESC + str(count) + 'B'


def cursor_forward(count=1):
    return ESC + str(count) + 'C'


def cursor_backward(count=1):
    return ESC + str(count) + 'D'


cursor_left = ESC + 'G'
cursor_save_position = ESC + ('7' if is_terminal_app else 's')
cursor_restore_position = ESC + ('8' if is_terminal_app else 'u')
cursor_get_position = ESC + '6n'
cursor_next_line = ESC + 'E'
cursor_prev_line = ESC + 'F'
cursor_hide = ESC + '?25l'
cursor_show = ESC + '?25h'


def erase_lines(count=1):
    clear = ''

    for i in range(count):
        clear += erase_line + (cursor_up() if i < count - 1 else '')

    return clear + cursor_left


def set_color(color):
    r, g, b = color
    return f'\u001B[38;2;{r};{g};{b}m'


def set_low_color(color_str):
    color_str_map = {
        'red': 91,
        'green': 92,
        'blue': 36,
        'gray': 97,
        'anti_red': 96,
        'anti_green': 95,
        'anti_blue': 93
    }
    return f'\u001B[{color_str_map[color_str]}m'


erase_end_line = ESC + 'K'
erase_start_line = ESC + '1K'
erase_line = ESC + '2K'
erase_down = ESC + 'J'
erase_up = ESC + '1J'
erase_screen = ESC + '2J'
scroll_up = ESC + 'S'
scroll_down = ESC + 'T'

clear_screen = '\u001Bc'
beep = '\u0007'
