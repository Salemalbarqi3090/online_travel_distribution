"""Utility for creating tagging data for sharing online travel experience"""
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.properties import ListProperty

#
# Templates of the text to be encoded in QR code
#


if platform == "android":
    from zbar import ZbarQrcodeDetector
    from .pydroid import share_intent

else:
    share_intent = None

    class ZbarQrcodeDetector(AnchorLayout):

        symbols = ListProperty([])

        def __init__(self, **kwargs):
            super(ZbarQrcodeDetector, self).__init__(**kwargs)

            box = BoxLayout()
            box.add_widget(Label(text="QR Scanner is only available on Android"))
            self.add_widget(box)

        def start(self):
            print "Start scanning ... Not supported"

        def stop(self):
            print "Stop scanning ... Not supported"


def share(subject, content):
    if share_intent:
        # Sharing for android
        share_intent(subject, content)
    else:
        raise NotImplementedError("Only available on Android")
