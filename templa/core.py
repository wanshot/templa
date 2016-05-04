# -*- coding: utf-8 -*-

import sys
import curses
import locale
import signal
import threading
import curses.ascii
import unicodedata

from manage import LoadConfig
from model import Model
from tty import get_ttyname, reconnect_descriptors

locale.setlocale(locale.LC_ALL, '')


class TerminateLoop(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Templa(object):

    def __init__(self, ret, f):
        self.global_lock = threading.Lock()
        self.model = Model(ret)
        self.conf = LoadConfig()
        self.y, self.x = 1, 0

        if f is None:
            self.stdin = sys.stdin
            self.stdout = sys.stdout
            self.stderr = sys.stderr
        else:
            self.stdin = f["stdin"]
            self.stdout = f["stdout"]
            self.stderr = f["stderr"]

    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.start_color()

        self.height, self.width = self.stdscr.getmaxyx()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

#         curses.curs_set(0)

        # Invalidation Ctrl + z
        signal.signal(signal.SIGINT, lambda signum, frame: None)
        self.stdscr.keypad(True)

        curses.raw()
        curses.noecho()
        curses.cbreak()
        curses.nonl()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        curses.nl()
        curses.endwin()

    # http://docs.python.jp/2/library/threading.html#timer-objects
    RE_DEPICTION_DELAY = 0.05

    def loop(self):
        # initialize
        self.refresh_display()
        self.updating_timer = None

        def re_despiction():
            self._set_prompt()
            self._set_lines()

        while True:
            try:
                key = self.stdscr.getch()

                if key == curses.KEY_DOWN:
                    self.y = self.model.next_line(self.y, self.x, self.height, self.width, curses.color_pair(1), self.stdscr)
                if key == curses.KEY_UP:
                    self.y = self.model.prev_line(self.y, self.x, self.height, self.width, curses.color_pair(1), self.stdscr)

                # normal key
                elif 0 < key < 256:
                    self.model.update(curses.ascii.unctrl(key))

                    if self.model.keyword:

                        with self.global_lock:

                            if key == ord("q"):
                                break

                            if self.updating_timer is not None:
                                # clear timer
                                self.updating_timer.cancel()
                                self.updating_timer = None
                            timer = threading.Timer(self.RE_DEPICTION_DELAY, re_despiction)
                            self.updating_timer = timer
                            timer.start()

                    self.refresh_display()
            except TerminateLoop as e:
                return e.value

    def refresh_display(self):
        with self.global_lock:
            self.y, self.x = 1, 0
            self.stdscr.erase()
            self._set_prompt()
            self._set_lines()
            self.stdscr.refresh()

    def _set_lines(self):
        for lineno, line in self.model.lines.items():
            adapt_line = self._adapt_line(line)
            if lineno == 1:
                self.stdscr.addstr(lineno, 0, adapt_line, curses.color_pair(1))  # set first line color
            else:
                self.stdscr.addstr(lineno, 0, adapt_line)
        self.stdscr.move(1, 3)

    def _set_prompt(self):
        # default prompt label
        label = '%'
        if self.conf.input_field_label:
            label = self.conf.input_field_label

        self.stdscr.addstr(0, 0, '{} {}'.format(label, self.model.keyword))

    def _adapt_line(self, line):
        ea_count = len([u for u in line.decode('utf-8') if unicodedata.east_asian_width(u) in ('F', 'W')])
        unicode_diff = len(line.decode('utf-8')) - ea_count
        diff_byte = self.width - (unicode_diff + (ea_count * 2))
        max_line = line + diff_byte * " "
        return max_line[:self.width]


class Core(object):

    def __init__(self, func,  **kwargs):
        self.list_ = func()

        ttyname = get_ttyname()

        with open(ttyname, 'r+w') as ttyfile:

            with Templa(self.list_, reconnect_descriptors(ttyfile)) as templa:
                value = templa.loop()
            sys.exit(value)


def deploy(*args, **kwargs):

    if len(args) == 1 and callable(args[0]):
        return Core(args[0], **kwargs)
