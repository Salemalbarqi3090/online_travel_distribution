import config
import pyrebase

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty
from kivy.storage.jsonstore import JsonStore

from .trip_manager import TripManager
from .trip_tracker import TripTracker
from .share_manager import ShareManager

class BackEndError(Exception):
    """Exception raised when having error with the backend database"""

    def __init__(self, error, cause=None):
        self.error = error
        self.cause = cause


class BackEndClient(EventDispatcher):
    """
    This system contains a back-end server that provides the registration and
    login service. This class wraps the operations of contacting the back-end
    server.

    In addition to the back-end server, data are synchronized to a Firebase
    database. This class also wraps the operations for synchronizing data
    with the Firebase database.
    """

    authenticated = BooleanProperty(False)

    def __init__(self, **kwargs):
        """Create a new client for accessing the back-end services."""
        super(BackEndClient, self).__init__(**kwargs)

        # User preferences
        self._local = JsonStore("onlinetravel.cache.json")

        # An instance of FirebaseApplication for accessing the
        # Firebase database. This is created after logged in
        firebase = pyrebase.initialize_app(config.FIREBASE)
        self._auth = firebase.auth()
        self._db = firebase.database()
        self._storage = firebase.storage()

        # Save the authenticated user
        self._uid = None        # UID of the user
        self._token = None      # Access token

        # Reference to the collections for the authenticated user
        self._trip_manager = None
        self._trip_tracker = None
        self._share_manager = None

    def on_authenticated(self, instance, authenticated):
        """Callback after authentication success to create necessary
        objects for authenticated user"""
        if authenticated:
            self._trip_manager = TripManager(self)
            self._trip_tracker = TripTracker(self)
            self._share_manager = ShareManager(self)
        else:
            self._trip_manager = None
            self._trip_tracker = None
            self._share_manager = None

    def auto_login(self):
        """
        Check local storage if a login session is valid.
        """
        if self._local.exists('session'):
            self._token = self._local['session']['token']

            # test if the token is still valid
            self._db.child("active").get(token=self._token)

            # get the user id
            resp = self._auth.get_account_info(self._token)
            self._uid = resp['users'][0]['localId']

            self.authenticated = True

        else:
            raise Exception("Session Expired")

    def login(self, email, password):
        """
        Signing in the back-end service using the given email/password.
        """
        try:
            user = self._auth.sign_in_with_email_and_password(email, password)

            # login success
            self._uid = user['localId']
            self._token = user['idToken']

            # Save login session in local preference
            self._local['session'] = {
                'token': self._token,
                'email': email
            }

            self.authenticated = True

        except Exception as e:
            if e.message.startswith('400'):
                error = "Incorrect email/password"
            else:
                error, _, _ = e.message.partition("http")
                error += "..."
            raise BackEndError(error=error, cause=e)

    def register(self, email, password):
        """
        Register a new account using the given email/password as the credentials.
        """
        try:
            self._auth.create_user_with_email_and_password(email, password)
        except Exception as e:
            if e.message.startswith('400'):
                error = "Email address has been taken"
            else:
                error, _, _ = e.message.partition("http")
                error += "..."
            raise BackEndError(error=error, cause=e)

    def session(self, key, default=None):
        if 'session' in self._local:
            if key in self._local['session']:
                return self._local['session'][key]
        return default

    def sign_out(self):
        """Invalidate the authentication token """
        if self._local.exists('session'):
            if 'token' in self._local['session']:
                del self._local['session']['token']
        self._uid = None
        self._token = None
        self.authenticated = False

    @property
    def uid(self):
        return self._uid

    @property
    def token(self):
        return self._token

    @property
    def db(self):
        return self._db

    @property
    def storage(self):
        return self._storage

    @property
    def trip_manager(self):
        return self._trip_manager

    @property
    def trip_tracker(self):
        return self._trip_tracker

    @property
    def share_manager(self):
        return self._share_manager
