from kivy.app import App
from kivy.logger import Logger

from .common import MyScreen, ListItem
from .popup import Alert, ConfirmPopup, QRPopup, SpinnerPopup, SelectorPopup

from utils.gmap import map_intent, geo_uri

from models.trip import TRANSPORTATIONS

class DestinationListItem(ListItem):
    """Represent an item in the destination list"""

    def update(self, attr):
        """Update an attribute of a destination trip"""

        app = App.get_running_app()
        screen = app.current_screen()
        trip_manager = app.backend.trip_manager

        if attr == 'day':
            prompt = 'Which day in your trip do you want to go to this destination?'
            current = self.item.day if self.item.day else 1
            options = ['{}'.format(i + 1) for i in range(app.trip.days)]
            converter = int
        elif attr == 'time':
            prompt = 'When do you want to go to this destination?'
            current = self.item.time if self.item.time else 'NA'
            options = ['{:02d}:00'.format(i) for i in range(24)]
            converter = str
        elif attr == 'transportation':
            prompt = 'How do you want to go to this destination?'
            current = self.item.transportation if self.item.transportation else 'plane'
            options = TRANSPORTATIONS
            converter = str
        else:
            return

        def callback(*args):
            """Callback to update the destination"""

            try:
                data = {attr: converter(args[1])}
                self.item.set(**data)

                trip_manager.update_destination(app.trip, self.item)

                app.destinations.sort()

                screen.reload()

            except Exception as e:
                Logger.exception('update destination')
                Alert(title=app.name, text=str(e))

        SelectorPopup(title="Update Destination", text=prompt,
                      options=options, initial=current,
                      on_value=callback)

    def generate_qrcode(self):
        """Generate QR code for this destination"""

        app = App.get_running_app()
        share_manager = app.backend.share_manager

        def callback(qr):
            return share_manager.upload_qrcode(self.item._id, qr)

        # Popup shows a QR code encoding the share url to the destination
        QRPopup(title="QR Tagging",
                text="Share your destination with other users",
                data=share_manager.share_url(app.trip, destination=self.item),
                share_callback=callback)

    def remove(self):
        """Remove the destination of this list item"""

        def callback(*args):
            """Callback when user confirms to delete"""
            app = App.get_running_app()
            screen = app.current_screen()
            trip_manager = app.backend.trip_manager

            try:
                # remove the trip from cloud
                trip_manager.delete_destination(app.trip, self.item)

                # remove from the local data
                app.trip._destinations.remove(self.item)

                # also remove the destination from the list view
                app.destinations.remove(self.item)

                screen.reload()

            except Exception as e:
                Logger.exception('delete_destination')
                Alert(title=self.name, text=str(e))

        ConfirmPopup(title="Delete Confirmation",
                     text="Do you want to remove '{}'?".format(self.item.name),
                     on_confirmed=callback)


class DestinationManager(MyScreen):
    """Represent the screen to manage destination of a trip"""

    def on_pre_enter(self, *args):
        # force updating list view
        self.reload()

    def reload(self):
        """force updating list view"""
        adapter = self.ids.listview.adapter
        prop = adapter.property('data')
        prop.dispatch(adapter)

    def get_recommendation(self):
        def callback(*args):
            app = App.get_running_app()

            lat = 0
            lon = 0
            for d in app.trip._destinations:
                lat += d.latitude
                lon += d.longitude
            lat /= len(app.trip._destinations)
            lon /= len(app.trip._destinations)

            try:
                map_intent(geo_uri(lat, lon, args[1]))
            except NotImplementedError as e:
                Alert(title="Recommendations", text=str(e))

        SpinnerPopup(title=self.title,
                     text="Which places are you looking for?",
                     options=['attraction', 'bar', 'hotel', 'restaurant', 'other'],
                     initial='hotel',
                     on_value=callback)

    def return_home(self):
        """Return home from the active trip"""

        app = App.get_running_app()
        trip_manager = app.backend.trip_manager

        def callback(*args):
            """Callback when user confirms to delete"""

            try:
                # set the trip as inactive
                trip_manager.set_active_trip(app.trip, active=False)
                app.active_trip = None
                app.screen_manager.back()

            except Exception as e:
                Logger.exception('inactive trip')
                Alert(title=self.name, text=str(e))

        ConfirmPopup(title="Return Home",
                     text="Do you want to finish '{}'?".format(app.trip.name),
                     on_confirmed=callback)