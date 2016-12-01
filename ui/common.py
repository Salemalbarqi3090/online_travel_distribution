from kivy.factory import Factory
from kivy.logger import Logger
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty, ListProperty

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.selectableview import SelectableView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton, ListItemLabel
from kivy.uix.bubble import BubbleButton
from kivy.uix.button import Button

#
# Common Widgets
#


class ScreenStackManager(ScreenManager):
    """
    Extends the implementation of ScreenManager to manage the order of showing
    screens as a stack.
    """

    has_back = BooleanProperty(False)

    def __init__(self, **kwargs):
        """Create a screen stack manager"""
        super(ScreenStackManager, self).__init__(**kwargs)

        self.screen_classes = {}

        # Managed loaded screen
        self.loaded_screens = {}

        # Stack of the screens that has been shown
        # with top of the screen is the current screen
        self._screen_stack = []
        # The screen that has just been hidden by going back
        self._recent_screen = None

    def register_screens(self, *screen_classes):
        for cls in screen_classes:
            self.screen_classes[cls.__name__] = cls

    def _load_screen(self, screen_name):
        if screen_name in self.loaded_screens:
            return self.loaded_screens[screen_name]

        cls = self.screen_classes[screen_name]
        screen = cls()

        self.loaded_screens[screen_name] = screen
        self.add_widget(screen)
        return screen

    def _push(self, screen):
        """Push a scren onto the screen stack"""
        self._screen_stack.append(screen)
        self.has_back = (len(self._screen_stack) > 1)

    def _pop(self):
        """Pop a screen from the stack"""
        screen = self._screen_stack.pop()
        self.has_back = (len(self._screen_stack) > 1)
        return screen

    def _top(self, replace_by=None):
        """Get or update the stack top"""
        if replace_by:
            self._screen_stack[-1] = replace_by
        else:
            return self._screen_stack[-1]

    def _switch(self, screen_name, direction=None):
        screen = self._load_screen(screen_name)
        #self.switch_to(screen, direction=direction)
        self.current = screen_name

    def show(self, screen, replace=False):
        """Go to the given screen, with the screen is pushed onto the stack"""
        screen_name = screen if type(screen) == str else screen.__name__
        #self.current = screen_name
        self._switch(screen_name, 'left')

        # update the screen stack
        if replace and len(self._screen_stack):
            self._top(screen_name)
        else:
            self._push(screen_name)

        self._recent_screen = None

    def back(self):
        """Go to previous screen in the stack"""
        if self.has_back:
            self._recent_screen = self._pop()
            #self.current = self._top()
            self._switch(self._top(), 'right')

    def forward(self):
        """Go to the recent screen"""
        if self._recent_screen:
            #self.current = self._recent_screen
            self._switch(self._recent_screen, 'left')

            # update the screen stack
            self._push(self._recent_screen)
            self._recent_screen = None


class MyScreen(Screen):
    """Base class for all screens"""

    # Title of the screen
    title = StringProperty()

    def __init__(self, **kwargs):
        super(MyScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        Logger.info("Screen: Enter %s", self.name)

    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(MyScreen, self).add_widget(*args)

    def reload(self):
        """Implement this method to dispatch properties to cause the view updated"""
        pass


class ListHeader(BoxLayout):
    """Represent the header of a list view"""

    # List of columns, each is a pair of (column_name, column_size)
    columns = ListProperty()

    def __init__(self, **kwargs):
        super(ListHeader, self).__init__(**kwargs)
        self.property('columns').dispatch(self)

    def on_columns(self, instance, columns):
        """Build the columns"""

        # total hint size
        total_size = 1.0 * sum(column[1] for column in columns)

        self.clear_widgets()

        # Add a label for header of each column
        for name, size in columns:
            self.add_widget(Factory.ListHeaderLabel(text=name,
                                                    size_hint_x=size/total_size))


class ListItem(SelectableView, BoxLayout):
    """Base class for a widget that is used as a list item"""

    index = NumericProperty()

    item = ObjectProperty()

    def __init__(self, **kwargs):
        super(ListItem, self).__init__(**kwargs)


class IconListItemButton(ListItemButton):
    """Icon button for a list item"""

    # Name of icon (FontAwesome icon)
    fa_icon = StringProperty('')

    # Subscript text for the item
    subscript = ObjectProperty('')


class IconListItemLabel(ListItemLabel):
    """Icon button for a list item"""

    # Name of icon (FontAwesome icon)
    fa_icon = StringProperty('')

    # Subscript text for the item
    subscript = ObjectProperty('')


class IconButton(Button):
    """Icon button"""

    # Label of the button
    label = StringProperty('')

    # Name of icon (FontAwesome icon)
    fa_icon = StringProperty('')

    # Subscript text for the item
    subscript = ObjectProperty('')


class IconBubbleButton(BubbleButton):
    """Icon bubble button"""

    # Name of icon (FontAwesome icon)
    fa_icon = StringProperty('')

    # Subscript text for the item
    subscript = ObjectProperty('')
