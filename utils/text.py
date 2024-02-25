from config import *

def text_color(text, color, is_bold = False):
    try:
        if is_bold:
            color_text = "{}{}{}{}".format(BOLD, color, text, RESET)
        else:
            color_text = "{}{}{}".format(color, text, RESET)

        return color_text
    except Exception as err:
        raise Exception("Failed to colort text") from err
