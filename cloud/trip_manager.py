import os

from .base import UserCollectionManager
from kivy.logger import Logger

from models.trip import Trip,  Destination, Note, Spent


def path_destinations(trip):
    """Helper functions to get the path where to save the destinations of a trip"""
    return "{}/destinations".format(trip._id)


def path_destination(trip, destination):
    """Helper functions to get the path where to save the destination of a trip"""
    return "{}/destinations/{}".format(trip._id, destination._id)


class TripManager(UserCollectionManager):
    """
    Provide a manager object that is used to access the trips database
    """

    def __init__(self, backend):
        """Create a manager to access the trips list of the authenticated user"""
        super(TripManager, self).__init__(backend, "trips")

    def get_user_trips(self):
        """Return all trips created by the authenticated user"""
        trips = []
        for item in self.list():
            try:
                trip = Trip(**item.val())
                trip._id = item.key()
                trips.append(trip)
            except Exception:
                Logger.exception("get_user_trips")

        return trips

    def add_trip(self, trip):
        """Create a new node for the given trip created by the authenticated user"""
        # Create new data node under "trips" path
        trip._id = self.push(trip.attrs)
        return trip

    def update_trip(self, trip, full_data=False):
        """Update data of the trip"""
        attrs = trip.full_data() if full_data else trip.attrs
        self.update(attrs, trip._id)

    def delete_trip(self, trip):
        """Remove the trip"""
        self.remove(trip._id)

    def set_active_trip(self, trip, active=True):
        """Set the trip as active"""
        trip.set(active=active)
        self.update({'active': active}, trip._id)

    def trip_destinations(self, trip):
        """Get destinations of the given trip"""

        destinations = []
        for item in self.list(path_destinations(trip)):
            try:
                dest = Destination(**item.val())
                dest._id = item.key()
                destinations.append(dest)
            except Exception:
                Logger.exception("trip_destinations")

        return destinations

    def add_destination(self, trip, destination):
        """Add a new destination for the given trip"""
        destination._id = self.push(destination.attrs, path_destinations(trip))
        return destination

    def update_destination(self, trip, destination):
        """Update the destination for the given trip"""
        self.update(destination.attrs, path_destination(trip, destination))

    def delete_destination(self, trip, destination):
        """Remove the destination from the given trip"""
        self.remove(path_destination(trip, destination))

    def add_note(self, trip, destination, note):
        """Add a note to the destination"""
        note._id = self.push(note.attrs, trip._id, 'destinations',
                             destination._id, 'notes')

    def remove_note(self, trip, destination, note):
        """Remove the note"""
        self.remove(trip._id, 'destinations', destination._id,
                    'notes', note._id)

    def update_note(self, trip, destination, note):
        """Update note's picture"""
        self.update(note.attrs, trip._id,
                    'destinations', destination._id,
                    'notes', note._id)

    def upload_image(self, note, file_path):
        """Upload images for a note"""
        _, ext = os.path.splitext(file_path)
        return self.put(file_path, note._id + ext)

    def add_spent(self, trip, destination, spent):
        """Add a spent to the destination"""
        spent._id = self.push(spent.attrs, trip._id, 'destinations',
                              destination._id, 'spents')

    def remove_spent(self, trip, destination, spent):
        """Remove the spent"""
        self.remove(trip._id,
                    'destinations', destination._id,
                    'spents', spent._id)

    def update_spent(self, trip, destination, spent):
        """Update spent"""
        self.update(spent.attrs, trip._id,
                    'destinations', destination._id,
                    'spents', spent._id)
