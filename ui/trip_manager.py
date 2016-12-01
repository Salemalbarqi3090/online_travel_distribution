from kivy.app import App
from kivy.logger import Logger

from .common import MyScreen, ListItem
from .popup import Alert, InputPopup, QRPopup, ConfirmPopup
from .trip_tracker import TripTracker

from models.trip import Trip


class TripListItem(ListItem):
    """Represent an item in the trip list"""

    def update(self, attr):
        """Update an attribute of the trip"""

        if attr == 'name':
            prompt = "Update name of your trip"
            current = self.item.name if self.item.name else ''
            input_filter = None
            input_converter = str

        elif attr == 'days':
            prompt = "Number of days for your trip"
            current = self.item.days if self.item.days else 1
            input_filter = 'int'
            input_converter = int

        else:
            return

        def callback(*args):
            """Callback to update the trip"""
            app = App.get_running_app()
            screen = app.current_screen()
            trip_manager = app.backend.trip_manager

            try:
                data = {attr: input_converter(args[1])}
                self.item.set(**data)

                trip_manager.update_trip(self.item)

                screen.reload()

            except Exception as e:
                Logger.exception('update trip')
                Alert(title=app.name, text=str(e))

        InputPopup(title="Update Trip", text=prompt,
                   initial=current, input_filter=input_filter,
                   on_value=callback)

    def generate_qrcode(self):
        """Generate QR code for this trip"""

        app = App.get_running_app()
        share_manager = app.backend.share_manager

        def callback(qr):
            return share_manager.upload_qrcode(self.item._id, qr)

        # Popup shows a QR code encoding the share url to the trip
        QRPopup(title="QR Tagging",
                text="Share your trip with other users",
                data=share_manager.share_url(self.item),
                share_callback=callback)

    def start(self):
        """Start tracking this trip"""
        app = App.get_running_app()

        if app.active_trip is not None:
            Alert(title="Start Trip",
                  text="You are now on another trip. "
                       "Please finish it first to start this trip")
            return

        # Set the trip as active
        trip_manager = app.backend.trip_manager
        trip_manager.set_active_trip(self.item)
        app.active_trip = self.item

        # Logger.info("Start Trip: %s", str(app.active_trip.__dict__))
        app.show('DestinationManager', trip=self.item)

    def remove(self):
        """Remove a trip"""

        def callback(*args):
            """Callback when user confirms to delete"""
            app = App.get_running_app()
            screen = app.current_screen()
            trip_manager = app.backend.trip_manager

            try:
                # remove the trip from cloud
                trip_manager.delete_trip(self.item)

                # also remove from the local list
                app.trips.remove(self.item)
                if app.trip == self.item:
                    app.trip = None

                screen.reload()

            except Exception as e:
                Logger.exception('delete_trip')
                Alert(title=self.name, text=str(e))

        ConfirmPopup(title="Delete Confirmation",
                     text="Do you want to remove '{}'?".format(self.item.name),
                     on_confirmed=callback)


class TripManager(MyScreen):
    """Represent the screen to manage trips created by the authenticated user"""

    def on_pre_enter(self, *args):
        # force updating list view
        self.reload()

    def reload(self):
        """force updating list view"""
        adapter = self.ids.listview.adapter
        prop = adapter.property('data')
        prop.dispatch(adapter)

    def add_trip(self):
        """Add new trip"""

        def callback(*args):
            """Callback to update the trip"""
            app = App.get_running_app()
            trip_manager = app.backend.trip_manager

            try:
                # create new trip
                trip = Trip(name=args[1], days=1)
                # add to data cloud
                trip_manager.add_trip(trip)
                # update the local data
                app.trips.append(trip)

                self.reload()

            except Exception as e:
                Logger.exception('add trip')
                Alert(title=app.name, text=str(e))

        InputPopup(title="Add Trip", text="Enter name of your trip", on_value=callback)
