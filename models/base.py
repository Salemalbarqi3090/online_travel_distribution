
class ModelBase(object):
    """Base class for all model objects"""

    def __init__(self, **kwargs):
        """Create an object with an id/key"""
        self._id = kwargs.get('_id', None)
        self.set(**kwargs)

    def set(self, **kwargs):
        pass

    def __getattr__(self, name):
        """Return an attribute of this object, None if the attribute does not exist"""
        try:
            return self.__dict__[name]
        except KeyError:
            return None

    @property
    def attrs(self):
        return dict((k, v) for k, v in self.__dict__.iteritems()
                    if not k.startswith('_'))
