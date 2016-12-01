"""
Utilities for accessing Python API via jnius module
"""

from jnius import autoclass, cast

# Autoclasses
PythonActivity = autoclass('org.renpy.android.PythonActivity')
Environment    = autoclass('android.os.Environment')
Intent         = autoclass('android.content.Intent')
File           = autoclass('java.io.File')
String         = autoclass('java.lang.String')
Uri            = autoclass('android.net.Uri')


# Helper functions

def CharSequence(s):
    """Convert a string into Java CharSequence"""
    return cast('java.lang.CharSequence', String(s))


def Parcelable(obj):
    """Case an object implemented Parcelable interface as a Parcelable instance"""
    return cast('android.os.Parcelable', obj)


def from_java_list(java_list):
    """Return a Python list from a Java list"""
    return [java_list.get(i) for i in range(java_list.size())]


def python_activity():
    """Get the current instance of PythonActivity"""
    return cast('android.app.Activity', PythonActivity.mActivity)


def uri_from_file(file_path):
    """Get Uri for the given file path"""
    file = File(String(file_path))
    return Uri.fromFile(file)


def internal_storage_path(filename):
    """Get the file path of the internal storage for the given filename"""
    current_activity = python_activity()
    my_file = File(current_activity.getFilesDir(), filename)
    return my_file.getPath()


def gallery_path():
    """Get path to the gallery"""
    dir = File(Environment.getExternalStorageDirectory(), Environment.DIRECTORY_DCIM)
    return dir.getPath()


def share_intent(subject, content, image_file=None):
    """Share content with Intents"""

    # create a new Android Intent for sending action
    intent = Intent()
    intent.setAction(Intent.ACTION_SEND)

    intent.putExtra(Intent.EXTRA_TEXT, CharSequence(content))

    if image_file:
        intent.putExtra(Intent.EXTRA_STREAM, Parcelable(uri_from_file(image_file)))
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.setType('image/*')
    else:
        intent.setType('text/plain')

    current_activity = python_activity()
    current_activity.startActivity(Intent.createChooser(intent, subject))
