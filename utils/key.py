from enum import Enum


class Key(Enum):
    """ Special keyboard keys enum """
    ENTER = [10]
    ESC = [27]
    ARROW_UP = [27, 91, 65]
    ARROW_DOWN = [27, 91, 66]
    ARROW_LEFT = [27, 91, 68]
    ARROW_RIGHT = [27, 91, 67]
    PAGE_UP = [27, 91, 53, 126]
    PAGE_DOWN = [27, 91, 54, 126]
    HOME = [27, 91, 72]
    END = [27, 91, 70]
    BACKSPACE = [127]
    INSERT = [27, 91, 50, 126]
    DELETE = [27, 91, 51, 126]

    ARROWS = [ARROW_UP, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT]

    def __repr__(self):  # pragma: no cover
        return self.nome + str(self.code)

    @property
    def code(self):  # pragma: no cover
        """
        The Key code

        :rtype: list[int]
        """
        return self.value if self != Key.ARROWS else []

    @staticmethod
    def get_key(code):
        """
        Return the Key mathing the code

        :param list[str] code:
        :rtype: Key
        """
        for t in Key:
            if t != Key.ARROWS and code == [chr(_c) for _c in t.code]:
                return t
