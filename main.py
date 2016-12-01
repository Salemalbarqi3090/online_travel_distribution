__version__ = "1.1.1"

from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ObjectProperty, ListProperty, StringProperty

import cloud
from models.trip import Trip, Destination

from ui.popup import Alert, ConfirmPopup

from ui.login import Login
from ui.home import Home

from ui.trip_manager import TripManager
from ui.destination_manager import DestinationManager
from ui.destination_editor import DestinationEditor
from ui.destination_notes import DestinationNotes
from ui.destination_spents import DestinationSpents


class MainApp(App):
    """
    Represent the Trip Planner application that allows user to create
    and manage their travel plan.
    """

    # The trip that the authenticated user is currently travelling
    active_trip = ObjectProperty(None, baseclass=Trip, allownone=True)

    # The destination that is being tracked
    tracked_destination = ObjectProperty(None, baseclass=Destination, allownone=True)

    # List of trips created by the user
    trips = ListProperty()

    # The trip that is being updated
    trip = ObjectProperty(None, baseclass=Trip, allownone=True)

    # List of destinations of the editing trip
    destinations = ListProperty()

    # The destination that is being updated
    destination = ObjectProperty(None, baseclass=Destination, allownone=True)

    # the client to access the back-end server
    backend = cloud.backend

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(kv_directory="ui", **kwargs)

    def build(self):
        """
        Build the application by adding all the screens required by
        the app.

        This build uses the GUI described in "main.kv" file
        (see the section marked by comment "# UI of the application")
        """
        self.title = 'Online Travel Distributor'

        # bind events
        self.backend.bind(authenticated=self.load_user_data)

        # Screens for the UI
        sm = self.root.ids.sm
        sm.register_screens(Login, Home, TripManager,
                            DestinationManager, DestinationEditor,
                            DestinationNotes, DestinationSpents)

        # Detect login session
        try:
            self.backend.auto_login()
            self.show(Home, True)
        except Exception as e:
            Logger.info('auto_login: %s', str(e))
            sm.show(Login)

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def current_screen(self):
        """Return the current screen from the screen manager"""
        return self.root.ids.sm.current_screen

    def get_screen(self, screen):
        """Return the screen associated with the given name"""
        return self.root.ids.sm.get_screen(screen if type(screen) == str else screen.__name__)

    def show(self, screen, replace=False, **kwargs):
        """Show the given screen"""
        for k, v in kwargs.iteritems():
            prop = self.property(k)
            prop.set(self, v)
        self.screen_manager.show(screen, replace)

    @property
    def screen_manager(self):
        return self.root.ids.sm

    def load_user_data(self, instance, authenticated):
        """Load user data after signed in"""

        if authenticated:
            trip_manager = self.backend.trip_manager

            try:
                self.trips = trip_manager.get_user_trips()
                for trip in self.trips:
                    if trip.active:
                        self.active_trip = trip
                        break

            except Exception as e:
                Logger.exception('load_user_data')
        else:
            self.trips = []
            self.active_trip = None

    def sign_out(self):
        """Clear the login session"""

        def callback(**args):
            """Callback when user confirms to sign out"""
            # sign out
            self.backend.sign_out()
            self.screen_manager.show(Login)

        ConfirmPopup(title="Sign Out", text="Are you sure to sign out?",
                     on_confirmed=callback)

    def on_trip(self, instance, trip):
        """Update the current destinations list when the editing trip is changed"""
        self.destinations = trip._destinations if trip and trip._destinations else []
        self.destinations.sort()


if __name__ == '__main__':
    # Run the app
    MainApp().run()
