# -*- coding: utf-8 -*-

import os
from ConfigParser import SafeConfigParser
from exceptions import ConfigLoadError

KUNAI_ROOT_DIRECTORY = os.path.expanduser('~/.kunai.d/')
KUNAI_CONF_PATH = KUNAI_ROOT_DIRECTORY + 'kunairc'

DEFAULT_CONFIG = """
[base]
KUNAI_FILE_PATH =

[shell executable]
SHELL = /bin/sh

[prompt]
# DEFAULT: `> `
INPUT_FIELD_LABEL =

[normal line options]
BOLD = False
UNDERLINE = False

[select line options]
BOLD = True
UNDERLINE = True

[normal line color]
TEXT = while
BACKGROUND = black

FG = white
BG = black

[select line color]
TEXT = while
BACKGROUND = blue

FG = white
BG = blue

[highlight color]
COLOR = yellow

[highlight options]
BOLD = True

[keymap]
UP = move_up
DOWN = move_down
LEFT = move_prev_page
RIGHT = move_next_page
BACKSPACE = backword_word
CTRL-c = exit_kunai
ENTER = select_line

"""

# TODO write debug method


def make_tempra_config_file():
    if not os.path.exists(KUNAI_ROOT_DIRECTORY):
        os.makedirs(KUNAI_ROOT_DIRECTORY)
    with open(KUNAI_CONF_PATH, 'w+') as f:
        f.write(DEFAULT_CONFIG)


class Config(object):
    """
    Q. Why are you divided the templarc and templa.py?
    A. Because I want to manage in the dotfiles
       There is a possibility that contain personal information is to templa.py
    """

    def __init__(self):
        self._check_config()
        self._load()

    def _check_config(self):
        if not os.path.exists(KUNAI_ROOT_DIRECTORY):
            raise ConfigLoadError('.kunai directory is not found')
        if not os.path.isfile(KUNAI_CONF_PATH):
            raise ConfigLoadError('kunairc is not found')

    def _load(self):
        conf = SafeConfigParser()
        conf.read(KUNAI_CONF_PATH)

        self.kunai_file_path = conf.get('base', 'KUNAI_FILE_PATH')
        self.input_field_label = conf.get('prompt', 'INPUT_FIELD_LABEL')
        self.shell = conf.get('shell executable', 'SHELL')

        self.normal_line_color = conf._sections['normal line color']
        self.select_line_color = conf._sections['select line color']

        self.normal_line_options = conf._sections['normal line options']
        self.select_line_options = conf._sections['select line options']

        self.highlight_color = conf.get('highlight color', 'COLOR')
        self.highlight_options = conf._sections['highlight options']

        self.keymap = conf._sections['keymap']


if __name__ == "__main__":
    print Config()
