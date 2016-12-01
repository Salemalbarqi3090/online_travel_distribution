import urllib

class CollectionManager(object):
    """
    Base class for a manager object that is used to access a cloud data
    under a given path.
    """

    def __init__(self, backend, *path):
        self._backend = backend
        self._db = backend.db
        self._storage = backend.storage
        self._token = backend.token
        self._path = list(path)

    def child(self, *path):
        return self._db.child(*self._path).child(*path)

    def push(self, data, *path):
        """Wrapper for FirebaseDatabase's push method"""
        resp = self.child(*path).push(data, token=self._token)
        return resp['name']

    def set(self, data, *path):
        """Wrapper for FirebaseDatabase's set method"""
        return self.child(*path).set(data, token=self._token)

    def update(self, data, *path):
        """Wrapper for FirebaseDatabase's update method"""
        return self.child(*path).update(data, token=self._token)

    def remove(self, *path):
        """Wrapper for FirebaseDatabase's remove method"""
        return self.child(*path).remove(token=self._token)

    def get(self, *path):
        """Wrapper for FirebaseDatabase's get method"""
        return self.child(*path).get(token=self._token)

    def val(self, *path):
        """Wrapper for FirebaseDatabase's get's val method"""
        data = self.child(*path).get(token=self._token)
        return data.val()

    def list(self, *path):
        """Wrapper for FirebaseDatabase's get's each method"""
        items = self.child(*path).get(token=self._token).each()
        if not items:
            items = []
        return items

    def list_by(self, key, value, *path):
        """Wrapper for FirebaseDatabase's get method with
        order_by_child and equal_to"""

        items = self.child(*path).order_by_child(key)\
                .equal_to(value).get(token=self._token).each()
        if not items:
            items = []
        return items

    def put(self, file, *path):
        """Wrapper for FirebaseStorage's put method"""
        resp = self._storage.child(*self._path).child(*path).put(file, token=self._token)
        if 'name' in resp:
            return self._storage.child(*self._path).child(*path).get_url()
        else:
            return ''
        # return "{}/o/{}?alt=media&token={}".format(self._storage.storage_bucket,
        #                                          urllib.quote(resp['name'], safe=''),
        #                                          resp['downloadTokens'])

    def get_file(self, *path):
        """Wrapper for FirebaseStorage's get method"""
        resp = self._storage.child(*path).get()
        print resp
        return resp


class UserCollectionManager(CollectionManager):
    """
    Provide a manager object that is used to access the trips database
    """

    def __init__(self, backend, *path):
        super(UserCollectionManager, self).__init__(backend, backend.uid, *path)

