# Package name which is used to deploy the application to Play Store
PACKAGE_NAME = "com.otd.onlinetraveller"

# Package name which is used to deploy the application to Play Store
APP_URL = "http://play.google.com/store/apps/details?id=" + PACKAGE_NAME

# Domain name for this application. This is used as URLs to share trip
# destinations
BACKEND_DOMAIN = "online-travel-server.herokuapp.com"
BACKEND_URL = "http://" + BACKEND_DOMAIN

# Configuration for Firebase Access
# Testing
# FIREBASE = {
#     "apiKey": "AIzaSyBv04aIdTmC7iZru0_6byazawy8aE1Z8mY",
#     "authDomain": "online-travel-distribution.firebaseapp.com",
#     "databaseURL": "https://online-travel-distribution.firebaseio.com",
#     "storageBucket": "online-travel-distribution.appspot.com",
# }

# Other
FIREBASE = {
    "apiKey": "AIzaSyB31vebzgbeOBSDPBMDNAqvEfwypbGr_ac",
    "authDomain": "online-travel-bd8d2.firebaseapp.com",
    "databaseURL": "https://online-travel-bd8d2.firebaseio.com",
    "storageBucket": "online-travel-bd8d2.appspot.com",
}
