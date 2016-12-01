"""
Utilities for accessing Google Map API via jnius module
"""
from kivy.logger import Logger
import urllib

try:
    from .pydroid import python_activity, Uri, Intent
except:
    python_activity = None


def geo_uri(lat, lng, query='', zoom=''):
    """Get the URI for display a map for the given location query"""
    return "geo:{},{}?q={}&z={}".format(lat, lng, urllib.quote(query), zoom)


def navigation_uri(target, mode='d'):
    """Get the URI for display a map for navigation to the target location"""
    try:
        lat, lng = target
        query = "{},{}".format(lat, lng)
    except:
        query = urllib.quote(target)

    return "google.navigation:q={}&mode={}".format(query, mode)


def map_intent(uri):
    """Launch the google map intent for the given uri"""

    Logger.info("map_intent: %s", str(uri))

    if not python_activity:
        raise NotImplementedError("Only available on Android")

    # Intent to launch GMap activity
    intent = Intent(Intent.ACTION_VIEW, Uri.parse(uri))
    intent.setPackage("com.google.android.apps.maps")

    # Launch the activity
    current_activity = python_activity()
    if intent.resolveActivity(current_activity.getPackageManager()):
        current_activity.startActivity(intent)
    else:
        raise NotImplementedError("Google Map is not available")
