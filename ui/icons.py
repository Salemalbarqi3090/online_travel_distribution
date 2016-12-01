import kivy
from kivy.resources import resource_find

kivy.resources.resource_add_path('data/fonts')


#
# Unicode for FontAwesome icons
#

class FontAwesomeIconDict(dict):
    def __missing__(self, key):
        return self.get('question')


def load_fontawesome_unichr():
    """
    Load FontAwesome icon names and their associated unicode
    """

    fa = FontAwesomeIconDict()

    with open(resource_find('FontAwesomeUnichr.txt'), 'Ur') as f:
        for line in f:
            k, _, v = line.partition(" ")
            fa[k] = unichr(int(v, 16))

    return fa


def fontawesome_markup(name, size=None, color=None):
    """
    Show an FontAwesome icon as a markup text. It can be used to show in icon
    in a markup text of a widget, e.g. Label, with 'markup' property set
    """

    return u"[font=FontAwesome.ttf]{size_open}{color_open}{icon}{color_close}{size_close}[/font]"\
        .format(size_open="[size={}]".format(size) if size is not None else "",
                size_close="[/size]" if size is not None else "",
                color_open="[color={}]".format(color) if color is not None else "",
                color_close="[/color]" if color is not None else "",
                icon=FontAwesomeIcons[name])


FontAwesomeIcons = load_fontawesome_unichr()
