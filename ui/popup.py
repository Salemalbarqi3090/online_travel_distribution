#
# Common Popups
#
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.popup import Popup
from utils import tagging

import os
try:
    from utils.pydroid import gallery_path
except:
    gallery_path = lambda: os.path.expanduser('~')



class Alert(Popup):
    """Represent a pop up that shows an alert"""
    text = StringProperty('No messages')
    dismiss_label = StringProperty('Dismiss')

    def __init__(self, **kwargs):
        super(Alert, self).__init__(**kwargs)
        self.open()


class ConfirmPopup(Popup):
    """Represent a pop up that shows a message for confirmation"""
    text = StringProperty('No messages')
    confirm_label = StringProperty('Ok')
    cancel_label = StringProperty('Cancel')
    confirmed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ConfirmPopup, self).__init__(**kwargs)

        on_confirmed = kwargs.get('on_confirmed', None)
        if on_confirmed is not None:
            self.bind(confirmed=lambda instance, value: on_confirmed())

        self.open()

    def dismiss(self, *args, **kwargs):
        """Dismiss the popup with confirmed set or not"""
        self.confirmed = True if kwargs.get("confirmed", False) else False
        super(ConfirmPopup, self).dismiss(*args, **kwargs)


class ImagePopup(Popup):
    """Represent a pop up that shows an alert"""
    message = StringProperty('No messages')
    dismiss_label = StringProperty('Dismiss')
    source = StringProperty()

    def __init__(self, **kwargs):
        super(ImagePopup, self).__init__(**kwargs)
        self.open()


class InputPopup(Popup):
    """Represent a pop up that shows a input field"""
    text = StringProperty('')
    confirm_label = StringProperty('Ok')
    cancel_label = StringProperty('Cancel')
    multiline = BooleanProperty(False)
    input_filter = ObjectProperty()
    value = ObjectProperty(None, allownone=True)
    initial = ObjectProperty('')

    def __init__(self, **kwargs):
        super(InputPopup, self).__init__(**kwargs)

        on_value = kwargs.get('on_value', None)
        if on_value is not None:
            self.bind(value=on_value)

        self.open()

    def dismiss(self, *args, **kwargs):
        """Dismiss the popup with value set to None"""
        self.value = self.ids.input_field.text if kwargs.get("confirmed", False) else None
        super(InputPopup, self).dismiss(*args, **kwargs)


class SelectorPopup(Popup):
    """Represent a pop up that shows a spinner for user to choose an option"""
    text = StringProperty('')
    confirm_label = StringProperty('Ok')
    cancel_label = StringProperty('Cancel')

    options = ListProperty()
    value = ObjectProperty(None, allownone=True)
    initial = ObjectProperty('')

    def __init__(self, **kwargs):
        super(SelectorPopup, self).__init__(**kwargs)

        on_value = kwargs.get('on_value', None)
        if on_value is not None:
            self.bind(value=on_value)

        self.open()

    def dismiss(self, *args, **kwargs):
        """Dismiss the popup with value set to None"""
        if kwargs.get("confirmed", False):
            self.value = self.ids.options.text
        else:
            self.value = None
        super(SelectorPopup, self).dismiss(*args, **kwargs)


class SpinnerPopup(Popup):
    """Represent a pop up that shows a input field"""
    text = StringProperty('')
    confirm_label = StringProperty('Ok')
    cancel_label = StringProperty('Cancel')

    options = ListProperty()
    value = ObjectProperty(None, allownone=True)
    initial = ObjectProperty('')
    other = ObjectProperty('')
    other_filter = ObjectProperty()

    def __init__(self, **kwargs):
        super(SpinnerPopup, self).__init__(**kwargs)

        on_value = kwargs.get('on_value', None)
        if on_value is not None:
            self.bind(value=on_value)

        self.open()

    def dismiss(self, *args, **kwargs):
        """Dismiss the popup with value set to None"""
        if kwargs.get("confirmed", False):
            value = self.ids.options.text
            if value == 'other':
                value = self.ids.other_value.text
            self.value = value
        else:
            self.value = None
        super(SpinnerPopup, self).dismiss(*args, **kwargs)


class ActionsPopup(Popup):

    text = StringProperty('')

    def __init__(self, **kwargs):
        super(ActionsPopup, self).__init__(**kwargs)
        self.open()

    def add_widget(self, widget):
        """Add widget to the container"""
        if self.content:
            self.content.add_widget(widget)
        else:
            super(ActionsPopup, self).add_widget(widget)


class ImageChooserPopup(Popup):
    """"""
    text = StringProperty('')
    confirm_label = StringProperty('Ok')
    cancel_label = StringProperty('Cancel')
    value = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(ImageChooserPopup, self).__init__(**kwargs)

        on_value = kwargs.get('on_value', None)
        if on_value is not None:
            self.bind(value=on_value)

        self.ids.filechooser.path = gallery_path()

        Logger.info('filechooser: %s', self.ids.filechooser.path)

        self.open()

    def dismiss(self, *args, **kwargs):
        """Dismiss the popup with value set to None"""
        if kwargs.get("confirmed", False):
            filechooser = self.ids.filechooser
            self.value = os.path.join(filechooser.path, filechooser.selection[0])
        else:
            self.value = None

        super(ImageChooserPopup, self).dismiss(*args, **kwargs)


class QRPopup(Popup):
    """Represent a pop up that shows a QR code"""
    text = StringProperty('No messages')
    share_label = StringProperty('Share')
    dismiss_label = StringProperty('Dismiss')

    title = StringProperty('')
    data = StringProperty('')

    share_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super(QRPopup, self).__init__(**kwargs)
        self.open()

    def dismiss(self, *args, **kwargs):
        """Share the QR code via a sharing facility, e.g. sharing intent
        on Android"""

        if kwargs.get("confirmed", False) and self.share_callback:
            url = self.share_callback(self.ids.qr_widget.qr.get_matrix())
            try:
                tagging.share(self.title, url)
            except NotImplementedError:
                Alert(title="Sharing Not Supported",
                      text="QR Code for this destination is available at " + str(url))

        super(QRPopup, self).dismiss(*args, **kwargs)


class QRDetectorPopup(Popup):
    """Represent a pop up that shows a QR code"""
    text = StringProperty('No messages')
    confirm_label = StringProperty('Ok')
    cancel_label = StringProperty('Cancel')
    data = StringProperty('')

    def __init__(self, **kwargs):
        super(QRDetectorPopup, self).__init__(**kwargs)

        on_detected = kwargs.get('detected', None)
        if on_detected:
            self.ids.detector.bind(symbols=on_detected)

        on_data = kwargs.get('on_data', None)
        if on_data is not None:
            self.bind(data=on_data)

        self.open()

    def dismiss(self, *args, **kwargs):
        """Dismiss the popup with value set to None"""
        # Stop the camera
        self.ids.detector.stop()

        # Save the data
        self.data = self.ids.data.text if kwargs.get("confirmed", False) else ''

        super(QRDetectorPopup, self).dismiss(*args, **kwargs)