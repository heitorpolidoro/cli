import atexit
import os
import time
from enum import Enum
from multiprocessing import Process


class Loading(object):
    """
    Print a loading animation in a separated process

    To change the default loading style use:
    Loading.style = STYLE

    To change the default interval use:
    Loading.interval = FLOAT
    """

    class Style(Enum):
        dots_fill_clockwise = "⠀⠈⠘⠸⢸⣸⣼⣾⣿⣷⣧⣇⡇⠇⠃⠁"
        square_small_clockwise = "⠋⠙⠚⠓"
        worm_3_dots_clockwise = "⠋⠙⠸⢰⣠⣄⡆⠇"
        worm_3_dots_anticlockwise = "⡆⣄⣠⢰⠸⠙⠋⠇"
        worm_4_dots_clockwise = "⡇⠏⠛⠹⢸⣰⣤⣆"

    step = 0
    processo = None
    style = None
    interval = 0.1

    @staticmethod
    def _hide_cursor():
        os.system('setterm -cursor off')
        atexit.register(Loading._show_cursor)

    @staticmethod
    def _show_cursor():
        os.system('setterm -cursor on')
        atexit.unregister(Loading._show_cursor)

    @staticmethod
    def start():
        """ Create and start the Loading process if there is none """
        if Loading.processo is None:
            Loading.processo = Process(target=Loading.run)
            Loading._hide_cursor()
            Loading.processo.start()
            atexit.register(Loading.stop)

    @staticmethod
    def stop():
        """ Stop and remove the Loading process """
        Loading.processo.terminate()
        Loading.processo = None
        atexit.unregister(Loading.stop)

    @staticmethod
    def run():
        """ The function to print the loading chars """
        if Loading.style is None:
            Loading.style = Loading.Style.worm_3_dots_clockwise
        try:
            while True:
                print(Loading.style.value[Loading.step], end='\r')
                Loading.step += 1
                if Loading.step == len(Loading.style.value):
                    Loading.step = 0
                time.sleep(Loading.interval)
        except KeyboardInterrupt:
            pass

    @staticmethod
    def show_all_styles():
        """ Show all available loading styles """
        Loading._hide_cursor()
        try:
            while True:
                for style in Loading.Style:
                    print(style.value[Loading.step % len(style.value)], style.name)
                    print()
                Loading.step += 1
                time.sleep(0.1)
                os.system('tput cuu %d' % (len(Loading.Style) * 2))
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    Loading.show_all_styles()
