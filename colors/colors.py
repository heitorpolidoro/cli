import os
import re
import sys


class ColorStdout(object):
    """
    Print wrapper to remove space between arguments comma separated and to force a Color_Off at the end of every print
    """

    def __init__(self):
        self.stdout = sys.stdout
        self.text = []

    def __getattr__(self, item):
        return getattr(self.stdout, item)

    def write(self, text):
        # Skip lone single spaces
        if text == ' ':
            return

        # Allow custom colors
        # $[f|b]number
        # f - foreground, b - background
        # number - 0..255
        if re.match('\$[fb](\d*)', text):
            # If is a match, get the color number and if fore ou back ground
            search = re.search('\$(?P<fb>[fb])(?P<color>\d*)', text).groupdict()
            # Generate de color char with tput
            color = os.popen("tput seta%s %s" % (search['fb'], search['color'])).read()
            # Append the color
            self.text.append(color)

        else:
            self.text.append(text)

        # If is a single '\n' print the text with Color_Off at the end
        if text in ('\n', '\r'):
            print(''.join(self.text), end=Color_Off, file=self.stdout)
            self.text = []

    def flush(self):
        if self.text:
            print(''.join(self.text), end=Color_Off, file=self.stdout)
            self.text = []
        self.stdout.flush()


# Replacing the current stdout
sys.stdout = ColorStdout()

# Reset
Color_Off = os.popen("tput sgr0").read()

# Formatting
Bold = os.popen("tput bold").read()
Dim = os.popen("tput dim").read()
BeginUnderline = os.popen("tput smul").read()
EndUnderline = os.popen("tput rmul").read()
Reverse = os.popen("tput rev").read()
Blinking = os.popen("tput blink").read()

# Regular Colors
Black = os.popen("tput setaf 0").read()
Red = os.popen("tput setaf 1").read()
Green = os.popen("tput setaf 2").read()
Yellow = os.popen("tput setaf 3").read()
Blue = os.popen("tput setaf 4").read()
Purple = os.popen("tput setaf 5").read()
Cyan = os.popen("tput setaf 6").read()
White = os.popen("tput setaf 7").read()

# Background
On_Black = os.popen("tput setab 0").read()
On_Red = os.popen("tput setab 1").read()
On_Green = os.popen("tput setab 2").read()
On_Yellow = os.popen("tput setab 3").read()
On_Blue = os.popen("tput setab 4").read()
On_Purple = os.popen("tput setab 5").read()
On_Cyan = os.popen("tput setab 6").read()
On_White = os.popen("tput setab 7").read()

# High Intensity
IBlack = os.popen("tput setaf 8").read()
IRed = os.popen("tput setaf 9").read()
IGreen = os.popen("tput setaf 10").read()
IYellow = os.popen("tput setaf 11").read()
IBlue = os.popen("tput setaf 12").read()
IPurple = os.popen("tput setaf 13").read()
ICyan = os.popen("tput setaf 14").read()
IWhite = os.popen("tput setaf 15").read()

# High Intensity backgrounds
On_IBlack = os.popen("tput setab 8").read()
On_IRed = os.popen("tput setab 9").read()
On_IGreen = os.popen("tput setab 10").read()
On_IYellow = os.popen("tput setab 11").read()
On_IBlue = os.popen("tput setab 12").read()
On_IPurple = os.popen("tput setab 13").read()
On_ICyan = os.popen("tput setab 14").read()
On_IWhite = os.popen("tput setab 15").read()

all_colors = [
    Bold, Dim, BeginUnderline, EndUnderline, Reverse, Blinking,
    Black,  On_Black,   IBlack,     On_IBlack,
    Red,    On_Red,     IRed,       On_IRed,
    Green,  On_Green,   IGreen,     On_IGreen,
    Yellow, On_Yellow,  IYellow,    On_IYellow,
    Blue,   On_Blue,    IBlue,      On_IBlue,
    Purple, On_Purple,  IPurple,    On_IPurple,
    Cyan,   On_Cyan,    ICyan,      On_ICyan,
    White,  On_White,   IWhite,     On_IWhite,
]
