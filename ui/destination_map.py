from kivy.app import App
from kivy.properties import ObjectProperty, NumericProperty

from .common import MyScreen

from models.trip import Destination


class DestinationMap(MyScreen):
    """Represent the screen to show a destination on a map"""

    # The destination being edited
    destination = ObjectProperty(None, allownone=True)

    latitude = NumericProperty()
    longitude = NumericProperty()

    def __init__(self, **kwargs):
        super(DestinationMap, self).__init__(name=DestinationMap.__name__,
                                             title='Destination Map', **kwargs)
        self.map_widget = self.ids.map_widget
        self.map_widget.bind(on_ready=self.on_map_widget_ready)

    def _load_data(self, *args):

        app = App.get_running_app()

        if app.current_destination is None:
            self.title = 'Add Destination'
            self.destination = Destination()
        else:
            self.title = 'Edit Destination'
            self.destination = app.current_destination

    def on_map_widget_ready(self, map_widget, *args):
        """When the map is ready to populate markers, etc"""
        map = map_widget.map

        location = map_widget.create_latlng(-33.867, 151.206)

        # map.setMyLocationEnabled(True)
        map.moveCamera(map_widget.camera_update_factory.newLatLngZoom(
            location, 13))

        marker = map_widget.create_marker(
            title='Test Marker',
            snippet='The most populous city in Autralia',
            position=location)
        map.addMarker(marker)

        # disable zoom button
        map.getUiSettings().setZoomControlsEnabled(False)

    def on_map_click(self, map_widget, latlng):
        self.latitude = latlng.latitude
        self.longitude = latlng.longitude
