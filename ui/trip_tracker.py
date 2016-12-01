from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ObjectProperty

from .common import MyScreen, ListItem
from .popup import Alert, ActionsPopup, SpinnerPopup, InputPopup, ConfirmPopup, QRPopup

from utils import iso_date, iso_date_string, today
from utils.gmap import map_intent, geo_uri, navigation_uri

from collections import defaultdict


class TrackedDestinationListItem(ListItem):
    """Represent an item in the destination list"""

    def arrive(self):
        """Update start date of this destination"""

        def callback(*args):
            """Callback to update start_date of the destination"""
            if args[1] is None:
                return  # cancel

            try:
                start_date = iso_date(args[1])
            except:
                Alert(title='Arrive Date', text="Please input a date in yyyy-mm-dd format")
                return

            self._update(start_date=iso_date_string(start_date))

        InputPopup(title='Arrive Date',
                   text='When did you arrive {}?'.format(self.item.name),
                   value=self.item.start_date,
                   initial=iso_date_string(today()),
                   on_value=callback)

    def leave(self):
        """Update end date of this destination"""

        def callback(*args):
            """Callback to update end_date of the destination"""
            if args[1] is None:
                return  # cancel

            try:
                end_date = iso_date(args[1])
            except:
                Alert(title='Leave Date', text="Please input a date in yyyy-mm-dd format")
                return

            self._update(end_date=iso_date_string(end_date))

        InputPopup(title='Leave Date',
                   text='When did you leave {}?'.format(self.item.name),
                   value=self.item.end_date,
                   initial=iso_date_string(today()),
                   on_value=callback)

    def _update(self, **kwargs):
        """Update this destination"""
        app = App.get_running_app()
        trip_tracker = app.backend.trip_tracker

        try:
            self.item.set(**kwargs)
            trip_tracker.update_destination(self.item)
        except Exception as e:
            Logger.exception('update_destination')
            Alert(title="Update Error", text=str(e))

        app.current_screen().reload()

    def show_info(self):
        """Popup show details of the place of this destination"""

        details = u"[b]{0[name]}[/b]\n" \
                  "Address: {0[address]}\n" \
                  "Phone Number: {0[phone_number]}\n" \
                  "Website: {0[website_uri]}\n" \
                  "[i]LatLng: ({0[latitude]}, {0[longitude]})[/i]"\
            .format(defaultdict(lambda: '', **self.item.attrs))

        DestinationActionsPopup(title=self.item.name,
                                text=details,
                                item=self.item)


class DestinationActionsPopup(ActionsPopup):
    """Popup that shows available actions for a chosen destination"""

    # The chosen destination
    item = ObjectProperty()

    def show_map(self):
        """Show the map for this place"""
        self.dismiss()

        try:
            map_intent(geo_uri(self.item.latitude, self.item.longitude, self.item.name))
        except NotImplementedError as e:
            Alert(title="Show Map", text=str(e))

    def show_navigation(self):
        """Show the turn-by-turn navigation from user current location to the destination"""
        self.dismiss()

        try:
            map_intent(navigation_uri((self.item.latitude, self.item.longitude)))
        except NotImplementedError as e:
            Alert(title="Show Navigation", text=str(e))

    def generate_qrcode(self):
        """Generate QR code for this destination"""
        self.dismiss()

        app = App.get_running_app()
        share_manager = app.backend.share_manager

        def callback(qr):
            return share_manager.upload_qrcode(self.item._id, qr)

        # Popup shows a QR code encoding the share url to the destination
        QRPopup(title="QR Tagging",
                text="Share your destination with other users",
                data=share_manager.share_url(app.active_trip, destination=self.item),
                share_callback=callback)

    def recommend(self):
        """Get recommendation of nearby places to visit"""
        self.dismiss()

        def callback(*args):
            try:
                map_intent(geo_uri(self.item.latitude, self.item.longitude, args[1]))
            except NotImplementedError as e:
                Alert(title="Recommendations", text=str(e))

        SpinnerPopup(title=self.title,
                     text="Which places are you looking for?",
                     options=['attraction', 'bar', 'hotel', 'restaurant', 'other'],
                     initial='hotel',
                     on_value=callback)


class TripTracker(MyScreen):
    """Represent the screen to manage trips created by the authenticated user"""

    def on_pre_enter(self, *args):
        """Update listview showing destinations of the active trip"""
        app = App.get_running_app()

        if app.active_trip._destinations is None:
            app.active_trip._destinations = []

        self.ids.listview.adapter.data = app.active_trip._destinations
        self.reload()

    def reload(self):
        """force updating list view"""
        adapter = self.ids.listview.adapter
        prop = adapter.property('data')
        prop.dispatch(adapter)

    def return_home(self):
        """Finish the active trip"""

        def callback(*args):
            """Callback to finish the trip after confirmation"""

            app = App.get_running_app()
            trip_manager = app.backend.trip_manager
            trip_tracker = app.backend.trip_tracker

            try:
                # Update budget base on actual spents
                app.active_trip.recalculate_budget()

                trip_manager.update_trip(app.active_trip, full_data=True)
                trip_tracker.remove()

                for i, trip in enumerate(app.trips):
                    if trip._id == app.active_trip._id:
                        app.trips[i] = app.active_trip
                        app.active_trip = None
                        break

                app.screen_manager.back()

            except Exception as e:
                Logger.exception('return_home')
                Alert(title=self.title, text=str(e))

        ConfirmPopup(title="Finish Trip",
                     text="Are you sure to finish this trip?",
                     on_confirmed=callback)

    def cancel_trip(self):
        """Cancel the active trip"""

        def callback(*args):
            """Callback to cancel the trip after confirmation"""

            app = App.get_running_app()
            trip_tracker = app.backend.trip_tracker

            try:
                trip_tracker.remove()
                app.active_trip = None
                app.screen_manager.back()

            except Exception as e:
                Logger.exception('cancel_trip')
                Alert(title=self.title, text=str(e))

        ConfirmPopup(title="Cancel Trip",
                     text="Are you sure to cancel this trip?",
                     on_confirmed=callback)
