from kivy.app import App

from .common import MyScreen
from .popup import Alert
from .home import Home

from cloud.backend import BackEndError


class Login(MyScreen):
    """Represent the screen to login"""

    def login(self):
        """
        Called when you click "Login" button on login screen to login
        to the back-end server.
        """
        app = App.get_running_app()

        try:
            app.backend.login(self.ids.email.text, self.ids.password.text)
            app.show(Home, True)

        except BackEndError as e:
            Alert(title="Login Error", text=e.error)
        except Exception as e:
            Alert(title="Login Error", text="Unexpected error: " + str(e))

    def register(self):
        """
        Called when you click "Register" button on login screen to register
        a new user account on the back-end server.
        """
        app = App.get_running_app()

        try:
            app.backend.register(self.ids.email.text, self.ids.password.text)
            Alert(title="Register Success", text="Your account is successfully created.")

        except BackEndError as e:
            Alert(title="Register Error", text=e.error)
        except Exception as e:
            Alert(title="Register Error", text="Unexpected error: " + str(e))
