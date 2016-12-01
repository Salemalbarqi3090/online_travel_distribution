from datetime import datetime
import png, io

#
# Format/Converter functions
#


def iso_date_string(date_obj):
    """Return the string representing the date in ISO format (yyyy-mm-dd)"""
    return date_obj.strftime('%Y-%m-%d')


def iso_date(date_str):
    """Return a date object from the string representing the date in ISO format"""
    return datetime.strptime(date_str, '%Y-%m-%d')


def today():
    """Get the today date"""
    return datetime.today()


#
# QR helper functions
#

def png_qr(qr_matrix):

    data = map(lambda row: map(lambda x: 0 if x else 1, row), qr_matrix)
    size = len(data)

    f = io.BytesIO()
    w = png.Writer(size, size, greyscale=True, bitdepth=1)
    w.write(f, data)
    content = f.getvalue()
    f.close()

    return io.BytesIO(content)



#
# Other helper functions
#

def find_one(function, iterable):
    """Find the first item in the iterable list which makes
    the function returns True"""

    for item in iterable:
        if function(item):
            return item

    return None
