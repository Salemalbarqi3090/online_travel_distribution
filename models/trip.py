from base import ModelBase


TRANSPORTATIONS = ['plane', 'train', 'ship', 'bus', 'car',
                   'motorcycle', 'bicycle', 'taxi', 'subway', 'walk']


class Trip(ModelBase):
    """Represent data of a trip"""

    def set(self, **kwargs):
        """Set data of a trip given its name, budget and stay days"""
        super(Trip, self).set(**kwargs)

        if 'name' in kwargs: self.name = kwargs['name']
        if 'days' in kwargs: self.days = kwargs['days']
        if 'active' in kwargs: self.active = kwargs['active']

        if 'destinations' in kwargs:
            self._destinations = [Destination(_id=key, **val)
                                  for key, val in kwargs['destinations'].iteritems()]
            self.calculate_budget()

    def full_data(self, with_id=True):
        data = dict(**self.attrs)
        if with_id:
            data['_id'] = self._id
        if self._destinations:
            data['destinations'] = dict((d._id, d.full_data(with_id=False)) for d in self._destinations)
        return data

    def calculate_budget(self):
        """Recalculate budget base on actual spents"""
        self.budget = 0
        for destination in self._destinations:
            destination.calculate_budget()
            self.budget += destination.budget

    def __str__(self):
        return self.name + ", stays: " + str(self.days)


class Place(ModelBase):
    """Wrapper for data of a place returned by Google Places API"""

    def set(self, **kwargs):
        """Set a place data with provided data"""
        super(Place, self).set(**kwargs)

        if 'address' in kwargs: self.address = kwargs['address']
        if 'attributions' in kwargs: self.attributions = kwargs['attributions']
        if 'id' in kwargs: self.id = kwargs['id']
        if 'latitude' in kwargs: self.latitude = kwargs['latitude']
        if 'longitude' in kwargs: self.longitude = kwargs['longitude']
        if 'name' in kwargs: self.name = kwargs['name']
        if 'phone_number' in kwargs: self.phone_number = kwargs['phone_number']
        if 'place_types' in kwargs: self.place_types = kwargs['place_types']
        if 'price_level' in kwargs: self.price_level = kwargs['price_level']
        if 'rating' in kwargs: self.rating = kwargs['rating']
        if 'website_uri' in kwargs: self.website_uri = kwargs['website_uri']


class Destination(Place):
    """Represent data of a destination, e.g. a place to visit/stay, in a trip"""

    def set(self, **kwargs):
        """Set a destination given its name, budget and stay days"""
        super(Destination, self).set(**kwargs)

        if 'day' in kwargs: self.day = kwargs['day']
        if 'time' in kwargs: self.time = kwargs['time']
        if 'transportation' in kwargs: self.transportation = kwargs['transportation']

        if 'notes' in kwargs:
            self._notes = [Note(_id=key, **val)
                           for key, val in kwargs['notes'].iteritems()]

        if 'spents' in kwargs:
            self._spents = [Spent(_id=key, **val)
                           for key, val in kwargs['spents'].iteritems()]
            self.calculate_budget()

    def full_data(self, with_id=True):
        data = dict(**self.attrs)
        if with_id:
            data['_id'] = self._id
        if self._notes:
            data['notes'] = dict((d._id, d.attrs) for d in self._notes)
        if self._spents:
            data['spents'] = dict((d._id, d.attrs) for d in self._spents)
        return data

    def calculate_budget(self):
        """Recalculate budget base on actual spents"""
        self.budget = 0
        if self._spents:
            for spent in self._spents:
                self.budget += spent.spent

    def __cmp__(self, other):
        """Compare this destination with the other by the the time order"""

        if other is None:
            return -1

        order = cmp(self.day, other.day)
        if order != 0:
            return order
        return cmp(self.time, other.time)


class Note(ModelBase):
    """Represent a note for a trip's destination"""

    def set(self, **kwargs):
        """Create a note given its content"""
        super(Note, self).set(**kwargs)

        if 'content' in kwargs: self.content = kwargs['content']
        if 'image' in kwargs: self.image = kwargs['image']


class Spent(ModelBase):
    """Represent a spent for a trip's destination"""

    def set(self, **kwargs):
        """Create a spent given its content"""
        super(Spent, self).set(**kwargs)

        if 'content' in kwargs: self.content = kwargs['content']
        if 'spent' in kwargs: self.spent = kwargs['spent']
