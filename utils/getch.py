import os
import sys

from utils.key import Key


class _Getch(object):  # pragma: no cover
    """ Gets a single character from standard input. Does not echo to the screen. """

    class _GetchTimeOutException(Exception):
        pass

    def __init__(self):
        import sys
        if not os.isatty(sys.stdin.fileno()):
            self.impl = _Getch.modo_debug
        else:
            try:
                # noinspection PyUnresolvedReferences
                import msvcrt
                self.impl = msvcrt.getch()

            except ImportError:
                def _getch():
                    import tty
                    import termios
                    old_settings = termios.tcgetattr(sys.stdin)
                    try:
                        tty.setcbreak(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    return ch[0]

                self.impl = _getch

    def __call__(self, block=True, translate_to_key=False, echo=False):
        if not block:
            if not os.isatty(sys.stdin.fileno()):
                return -1
                # return _Getch.modo_debug()
            else:
                import signal
                signal.signal(signal.SIGALRM, _Getch.alarm_handler)
                signal.setitimer(signal.ITIMER_REAL, 0.01)
                try:
                    resp = self.impl()
                    signal.alarm(0)
                except _Getch._GetchTimeOutException:
                    signal.signal(signal.SIGALRM, signal.SIG_IGN)
                    resp = -1
        elif translate_to_key:
            commands = []
            resp = self.impl()
            while resp != -1:
                commands.append(resp)
                resp = self(False)
            key = Key.get_key(commands)
            if key:
                resp = key
            elif len(commands) == 1:
                resp = commands[0]
            elif commands:
                resp = commands
        else:
            resp = self.impl()

        if echo:
            if resp not in Key:
                print(resp, end='', flush=True)
        return resp

    @staticmethod
    def modo_debug() -> str:
        """ Uses input to simulate getch """
        code = []  # type list[str]
        resp = input().strip(' ')
        if resp:
            if len(resp) > 1 and resp.startswith('n') and (resp[1:].isdigit() or resp[1] == '-' and resp[2:].isdigit()):
                code = [chr(int(resp[1:]))]
            elif resp.startswith('t'):
                if resp in ['tAD']:  # Atalhos
                    code = [chr(_c) for _c in Key.ARROW_DOWN.code]
                elif resp in ['tAU']:  # Atalhos
                    code = [chr(_c) for _c in Key.ARROW_UP.code]
                elif resp in ['tAL']:  # Atalhos
                    code = [chr(_c) for _c in Key.ARROW_LEFT.code]
                elif resp in ['tAR']:  # Atalhos
                    code = [chr(_c) for _c in Key.ARROW_RIGHT.code]
                elif resp in ['tE']:  # Atalhos
                    code = [chr(_c) for _c in Key.ENTER.code]
                elif resp in ['tES']:  # Atalhos
                    code = [chr(_c) for _c in Key.ESC.code]
                else:
                    for t in Key:
                        if t.name == resp[1:]:
                            code = [chr(_c) for _c in t.code]
                            break
            else:
                code = [resp]
        else:
            code = ['']

        return code[0]

    @staticmethod
    def alarm_handler(signum, frame):
        raise _Getch._GetchTimeOutException


def getch(block: bool = True, translate_to_key: bool = False):  # pragma: no cover
    """
    Gets a single character from standard input. 
    Does not echo to the screen.

    :param block: If wait for the input, if false return -1 if nothing is pressed
    :param translate_to_key: Return the Key, if any special key is pressed.
    :rtype: str | Key
    """
    # noinspection PyProtectedMember
    return _Getch()(block=block, translate_to_key=translate_to_key)


def getche(block: bool = True, translate_to_key=False):  # pragma: no cover
    """
    Gets a single character from standard input. 
    Echoing to the screen.

    :param block: If wait for the input, if false return -1 if nothing is pressed
    :param translate_to_key: Return the Key, if any special key is pressed.
    :rtype: str | Key
    """
    # noinspection PyProtectedMember
    return _Getch()(block=block, translate_to_key=translate_to_key, echo=True)
