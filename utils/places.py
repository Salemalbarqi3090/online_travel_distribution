"""
Utilities for accessing Google Places API via jnius module
"""
from kivy.logger import Logger

try:
    from jnius import autoclass
    from android import activity

    from .pydroid import python_activity, from_java_list

    # Autoclasses
    PlacePicker = autoclass('com.google.android.gms.location.places.ui.PlacePicker')
    PlacePickerIntentBuilder = autoclass('com.google.android.gms.location.places.ui.PlacePicker$IntentBuilder')

except:
    python_activity = None


PLACE_PICKER_REQUEST = 1
RESULT_OK = -1


def place_picker(on_place_return):
    """
    Launch Google's PlacePicker intent for user choosing a place.
    User chosen place is returned via the given callback.
    """

    if not python_activity:
        raise NotImplementedError("Only available on Android")

    # The Python activity
    current_activity = python_activity()

    # Create intent to PlacePicker
    builder = PlacePickerIntentBuilder()
    intent = builder.build(current_activity)

    def result_callback(requestCode, resultCode, data):
        """Callback for getting activity result"""
        if requestCode == PLACE_PICKER_REQUEST:
            if resultCode == RESULT_OK:
                place = PlacePicker.getPlace(data, current_activity)
                Logger.info("PlacePicker: %s", str(place))

                on_place_return(extract_from_google_place(place))
            else:
                on_place_return(None)

    activity.bind(on_activity_result=result_callback)
    current_activity.startActivityForResult(intent, PLACE_PICKER_REQUEST)


def extract_from_google_place(place):
    """Create a dict object containing data extracted from a place data
    returned by Google API"""

    data = {}
    for key in ('address', 'attributions', 'id', 'lat_lng', 'name',
                'phone_number', 'place_types', 'price_level', 'rating', 'website_uri'):
        try:
            getter = 'get' + ''.join([w.capitalize() for w in key.split('_')])
            data[key] = getattr(place, getter)()
        except Exception as e:
            Logger.error('Place: %s %s', getter, str(e))

    if data.get('place_types', None):
        data['place_types'] = from_java_list(data['place_types'])
    if data.get('lat_lng', None):
        data['latitude'] = data['lat_lng'].latitude
        data['longitude'] = data['lat_lng'].longitude
    if data.get('website_uri', None):
        data['website_uri'] = data['website_uri'].toString()

    return data
