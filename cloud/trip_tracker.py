from .base import UserCollectionManager
from kivy.logger import Logger

from models.trip import Trip,  Destination, Note, Spent

import os


class TripTracker(UserCollectionManager):
    """
    Provide a manager object for tracking user trips
    """

    def __init__(self, backend):
        super(TripTracker, self).__init__(backend, 'active')

    def start_trip(self, trip):
        """Set the given trip as active"""
        data = trip.full_data()
        self.set(data)
        return Trip(**data)

    def get_active_trip(self):
        """Get the trip that the authenticated user is currently traveling on"""
        val = self.val()
        if val is not None:
            return Trip(**val)
        else:
            return None

    def update_destination(self, destination):
        """Update the destination to the active trip"""
        self.update(destination.attrs, 'destinations', destination._id)

    def add_note(self, destination, note):
        """Add a note to the destination"""
        note._id = self.push(note.attrs, 'destinations', destination._id, 'notes')

    def remove_note(self, destination, note):
        """Remove the note"""
        self.remove('destinations', destination._id, 'notes', note._id)

    def update_note(self, destination, note):
        """Update note's picture"""
        self.update(note.attrs, 'destinations', destination._id, 'notes', note._id)

    def upload_image(self, note, file_path):
        """Upload images for a note"""
        _, ext = os.path.splitext(file_path)
        return self.put(file_path, note._id + ext)

    def add_spent(self, destination, spent):
        """Add a spent to the destination"""
        spent._id = self.push(spent.attrs, 'destinations', destination._id, 'spents')

    def remove_spent(self, destination, spent):
        """Remove the spent"""
        self.remove('destinations', destination._id, 'spents', spent._id)

    def update_spent(self, destination, spent):
        """Update spent"""
        self.update(spent.attrs, 'destinations', destination._id, 'spents', spent._id)



    def get_notes(self, destination):
        """Get notes for a destination"""

        notes = []
        for item in self.list('destinations', destination._id, 'notes'):
            try:
                note = Note(**item.val())
                note._id = item.key()
                notes.append(note)
            except Exception:
                Logger.exception("get_notes")

        return notes

    def get_destinations(self):
        """Get destinations list of the active trip"""
        destinations = []
        for item in self.list("destinations"):
            try:
                dest = Destination(**item.val())
                dest._id = item.key()
                destinations.append(dest)
            except Exception:
                Logger.exception("trip_destinations")

        # sort by start_date
        destinations.sort()

        return destinations

    def add_destination(self, destination):
        """Add a destination to the active trip"""
        self.set(destination.attrs, 'destinations/' + str(destination._id))
