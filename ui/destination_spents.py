from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ListProperty

from .common import MyScreen, ListItem
from .popup import Alert, ImagePopup, InputPopup, SpinnerPopup, ConfirmPopup, ImageChooserPopup

from models.trip import Spent


class SpentListItem(ListItem):
    """Represent an item in the spent list"""

    def update_spent(self):
        """Update money spent for this destination"""

        def callback(*args):
            """Callback for input popup to set destination's spent"""
            if args[1] is None:
                return  # cancel

            app = App.get_running_app()

            try:
                spent = int(args[1])
                if spent < 0:
                    raise Exception

                self.item.set(spent=spent)
                app.current_screen().update_spent(self.item)
                app.current_screen().reload()

            except:
                Alert(title='Update Spent', text="Please input an integral amount")
                return

        # input dialog for user enter the spent amount
        InputPopup(title="Update Spent",
                   text="How much ($) have you spent for {}?".format(self.item.content),
                   value=self.item.spent,
                   initial='0',
                   on_value=callback)

    def remove(self):
        """Remove the spent associated with this list item"""
        app = App.get_running_app()
        app.current_screen().remove_spent(self.item)


class DestinationSpents(MyScreen):
    """Represent the screen to manage spents of a tracked destination"""

    spents = ListProperty()

    def on_pre_enter(self, *args):
        """Update listview showing spents of a destination"""
        app = App.get_running_app()

        if app.destination._spents is None:
            app.destination._spents = []

        self.spents = app.destination._spents

    def on_pre_leave(self, *args):
        """Update the spents of the tracked destination"""
        app = App.get_running_app()
        app.destination._spents = self.spents

    def reload(self):
        """force updating list view"""
        adapter = self.ids.listview.adapter
        prop = adapter.property('data')
        prop.dispatch(adapter)

    def add_spent(self):
        """Add a note for the current destination"""
        app = App.get_running_app()
        trip_manager = app.backend.trip_manager

        def callback(*args):
            """Callback for input popup to add new note"""
            content = args[1]
            if content is None:
                return

            try:
                # add to the cloud
                spent = Spent(content=content, spent=0)
                trip_manager.add_spent(app.trip, app.destination, spent)

                # update the local list
                self.spents.append(spent)

            except Exception as e:
                Logger.exception('add_spent')
                Alert(title=self.title, text=str(e))

        # input dialog for user enter a spent
        InputPopup(title="Add Spent",
                   text="What did you spent for " + str(app.destination.name),
                   multiline=True,
                   on_value=callback)

    def remove_spent(self, spent):
        """Remove a spent for the current destination"""

        def callback():
            """Callback for delete a spent after confirmation """

            app = App.get_running_app()
            trip_manager = app.backend.trip_manager

            try:
                # remove the spent from the cloud
                trip_manager.remove_spent(app.trip, app.destination, spent)

                # update the local list
                self.spents.remove(spent)

            except Exception as e:
                Logger.exception('remove_spent')
                Alert(title=self.title, text=str(e))

        ConfirmPopup(title="Delete Spent",
                     text="Do you want to remove this spent?",
                     on_confirmed=callback)

    def update_spent(self, spent):
        """Update a spent for the current destination"""

        app = App.get_running_app()
        trip_manager = app.backend.trip_manager

        try:
            trip_manager.update_spent(app.trip, app.destination, spent)
        except Exception as e:
            Logger.exception('update_spent')
            Alert(title=self.title, text=str(e))
