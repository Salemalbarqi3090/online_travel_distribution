from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ListProperty

from .common import MyScreen, ListItem
from .popup import Alert, ImagePopup, InputPopup, SpinnerPopup, ConfirmPopup, ImageChooserPopup

from models.trip import Note


class NoteListItem(ListItem):
    """Represent an item in the note list"""

    def view(self):
        """View image of the note, or upload another one"""
        try:
            ImagePopup(title="Note", message=self.item.content,
                       source=self.item.image if self.item.image else '')

        except Exception as e:
            Logger.exception('upload_image')
            Alert(title="Upload Image", text=str(e))

    def edit(self):
        """Update a note for the current destination"""

        app = App.get_running_app()

        def callback(*args):
            self.item.content = args[1]
            app.current_screen().update_note(self.item)

        # input dialog for user enter a note
        InputPopup(title="Update Note",
                   text="Update note for " + str(app.destination.name),
                   initial=self.item.content, multiline=True,
                   on_value=callback)

    def choose_image(self):
        """Change image for the note"""

        def callback(*args):
            """Callback for upload picture after confirmation"""
            file_path = args[1]

            app = App.get_running_app()
            trip_manager = app.backend.trip_manager

            try:
                self.item.image = trip_manager.upload_image(self.item, file_path)
                app.current_screen().update_note(self.item)

            except Exception as e:
                Logger.exception('upload_image')
                Alert(title="Upload Image", text=str(e))

        ImageChooserPopup(title="Choose Note Image",
                          text="Please choose an image for your note",
                          on_value=callback)

    def remove(self):
        """Remove the note associated with this list item"""
        app = App.get_running_app()
        app.current_screen().remove_note(self.item)


class DestinationNotes(MyScreen):
    """Represent the screen to manage notes of a tracked destination"""

    notes = ListProperty()

    def on_pre_enter(self, *args):
        """Update listview showing destinations of the active trip"""
        app = App.get_running_app()

        if app.destination._notes is None:
            app.destination._notes = []

        self.notes = app.destination._notes

    def on_pre_leave(self, *args):
        """Update the notes of the tracked destination"""
        app = App.get_running_app()
        app.destination._notes = self.notes

    def reload(self):
        """force updating list view"""
        adapter = self.ids.listview.adapter
        prop = adapter.property('data')
        prop.dispatch(adapter)

    def add_note(self):
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
                note = Note(content=content)
                trip_manager.add_note(app.trip, app.destination, note)

                # update the local list
                self.notes.append(note)

            except Exception as e:
                Logger.exception('add_note')
                Alert(title=self.title, text=str(e))

        # input dialog for user enter a note
        InputPopup(title="Add Note",
                   text="Add note for " + str(app.destination.name),
                   multiline=True,
                   on_value=callback)

    def remove_note(self, note):
        """Remove a note for the current destination"""

        def callback():
            """Callback for delete a note after confirmation """

            app = App.get_running_app()
            trip_manager = app.backend.trip_manager

            try:
                # remove the note from the cloud
                trip_manager.remove_note(app.trip, app.destination, note)

                # update the local list
                self.notes.remove(note)

            except Exception as e:
                Logger.exception('remove_note')
                Alert(title=self.title, text=str(e))

        ConfirmPopup(title="Delete Note",
                     text="Do you want to remove this note?",
                     on_confirmed=callback)

    def update_note(self, note):
        """Update a note for the current destination"""

        app = App.get_running_app()
        trip_manager = app.backend.trip_manager

        try:
            trip_manager.update_note(app.trip, app.destination, note)
            self.reload()
        except Exception as e:
            Logger.exception('update_note')
            Alert(title=self.title, text=str(e))
