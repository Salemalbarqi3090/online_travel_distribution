import config
from urlparse import urlparse
from utils import png_qr

from .base import CollectionManager
from models.trip import Trip, Destination, Note


class ShareManager(CollectionManager):
    """
    Provide a manager object that is used to access the trips database
    shared by all users
    """

    def __init__(self, backend):
        """Create an instance of ShareManager"""
        super(ShareManager, self).__init__(backend)

    def share_url(self, trip, destination=None, note=None):
        """Get the url for sharing the given object, e.i. trip, destination, or note"""

        path = ['', self._backend.uid, trip._id]
        query = 'trip'
        if destination:
            path.append(destination._id)
            query = 'destination'
        if note:
            path.append(note._id)
            query = 'note'

        return config.BACKEND_URL + '/'.join(path) + '?' + query

    def get_by_url(self, url, validation=None):
        """Get the object given in the URL, which is generated by 'share_url' method"""
        r = urlparse(url)
        if r.netloc == config.BACKEND_DOMAIN:
            if r.query == 'trip':
                # path to access the trip
                _, uid, trip_id = r.path.split('/')
                if validation is not None and validation == 'trip':
                    return True

                # Query the Trip object at given path
                data = self.val(uid, 'trips', trip_id)
                return Trip(_id=trip_id, **data)

            elif r.query == 'destination':
                # path to access the destination
                _, uid, trip_id, destination_id = r.path.split('/')
                if validation is not None and validation == 'destination':
                    return True

                # Query the Destination object at given path
                data = self.val(uid, 'trips', trip_id,
                                'destinations', destination_id)
                return Destination(_id=destination_id, **data)

            elif r.query == 'note':
                # path to access the note
                _, uid, trip_id, destination_id, note_id = r.path.split('/')
                if validation is not None and validation == 'note':
                    return True

                # Query the Note object at given path
                data = self.val(uid, 'trips', trip_id,
                                'destinations', destination_id,
                                'notes', note_id)
                return Note(_id=note_id, **data)

        raise ValueError, 'invalid url'

    def upload_qrcode(self, obj_id, qr_matrix):
        img = png_qr(qr_matrix)
        return self.put(img, 'shared', obj_id + '.png')
