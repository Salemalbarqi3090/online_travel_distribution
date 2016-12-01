from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty

from .common import MyScreen
from .popup import Alert, QRDetectorPopup

from models.trip import Destination, Place
from utils.places import place_picker

from collections import defaultdict


class DestinationEditor(MyScreen):
    """Represent the screen to add/edit a destination to a trip"""

    place_data = ObjectProperty()

    def on_pre_enter(self, *args):
        app = App.get_running_app()

        if app.destination:
            self.place_data = Place(**app.destination.attrs).attrs
        else:
            self.place_data = {}

    def save(self):
        """Create new destination or update the current destination"""

        app = App.get_running_app()
        trip_manager = app.backend.trip_manager

        # Update the destination
        destination = app.destination if app.destination else Destination()
        destination.set(**self.place_data)

        if app.destination:
            # update current destination
            trip_manager.update_destination(app.trip, destination)
        else:
            # create a new destination
            app.destination = trip_manager.add_destination(app.trip, destination)

            if app.trip._destinations is None:
                app.trip._destinations = []
            app.trip._destinations.append(app.destination)

            app.destinations.append(app.destination)
            app.destinations.sort()

        app.screen_manager.back()

    def pick_place(self):

        def callback(place_data):
            """Callback when user has picked a place"""
            Logger.info("Place data: %s", str(place_data))
            self.place_data = place_data

        try:
            place_picker(callback)
        except NotImplementedError as e:
            Alert(title=self.title, text=str(e))

    def scan_qrcode(self):
        """Scan QR code for importing a destination"""

        app = App.get_running_app()
        share_manager = app.backend.share_manager

        def validate(instance, symbols):

            url = "".join(symbols)
            try:
                share_manager.get_by_url(url, validation='destination')
                instance.dismiss(confirmed=True)
            except Exception as e:
                Logger.info("Invalid URL detected %s", url)

        def callback(*args):
            try:
                destination = share_manager.get_by_url(args[1])
                if not isinstance(destination, Destination):
                    raise ValueError, 'Not a destination url'

                self.place_data = Place(**destination.attrs).attrs

            except Exception as e:
                Logger.exception('scan_qrcode')
                Alert(title=self.title, text="Invalid URL")

        QRDetectorPopup(title="QR Tagging",
                        text="Scan QR code for a travel destination",
                        on_detected=validate,
                        on_data=callback)

    def place_summary(self):
        """Return string summarized of the place data to show"""
        return u"[b]{0[name]}[/b]\n" \
               "Address: {0[address]}\n" \
               "Phone Number: {0[phone_number]}\n" \
               "Website: {0[website_uri]}\n" \
               "[i]LatLng: ({0[latitude]}, {0[longitude]})[/i]"\
            .format(defaultdict(lambda: '', **self.place_data))
