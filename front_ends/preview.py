"""
`front_ends/preview.py`
\nThis module consists of `Preview` which is a preview page let user preview/ confirm before adding to the database.
"""

from library.logic.database import update_database
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
import os


class Preview(Widget):
    """
    A page let user preview everything before adding to the database.
    """

    id = 'preview'
    photo = ObjectProperty(None)
    ti_word = ObjectProperty(None)
    ti_definition = ObjectProperty(None)
    ti_example = ObjectProperty(None)
    speaker = ObjectProperty(None)
    
    def __init__(self):
        super(Preview, self).__init__()
        self.is_photo = True

    def go_back(self) -> None:
        """
        Callback method from Go-Back Button. Redirect to [`AddVocab`](/reference/#front_ends.add_vocab.AddVocab) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('add_vocab')
        )

    def refresh_gui(self) -> None:
        """
        Called by [`AddVocab.update_database`](/reference/#front_ends.add_vocab.AddVocab.update_database). Show photo, set sound
        and information of the word in the user interface.
        """
        self.show_photo(Widget())
        self.set_text_input()
        self.set_sound()

    def show_photo(self, instance: Widget) -> None:
        """
        Show photo of the word in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.is_photo = False
        self.change_photo(Widget())

    def set_text_input(self) -> None:
        """
        Show information according to the [`AddVocab`](/reference/#front_ends.add_vocab.AddVocab) page.
        """
        slide_vocab = App.get_running_app().__getattribute__('add_vocab')
        self.ti_word.text = slide_vocab.lbl_word.text.strip()
        self.ti_definition.text = slide_vocab.ti_def.text.strip()
        self.ti_example.text = slide_vocab.ti_example.text.strip()

    def set_sound(self) -> None:
        """
        Set speaker color in the user interface and play the sound file if available.
        """
        dimming_color = (0.3, 0.3, 0.3, 0.5)
        normal_color = (1.0, 1.0, 1.0, 1.0)

        slide_add_vocab = App.get_running_app().__getattribute__('add_vocab')
        if slide_add_vocab.sound:
            color = normal_color
            file = os.path.join(App.get_running_app().working_dir, 'library', 'sounds', 'temp.mp3')
            player = SoundLoader.load(file)
            player.play()
        else:
            color = dimming_color

        self.speaker.background_color = color

    def change_photo(self, instance: Widget) -> None:
        """
        Change the photo to 'No Photo' or 'selected photo' in the user interface.

        Args:
             instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        # define directory and file
        working_dir = os.path.join(App.get_running_app().working_dir)
        no_photo = os.path.join(working_dir, 'library', 'images', 'no_image.png')
        photo = App.get_running_app().__getattribute__('select_photo').photo_to_be_added

        # change photo
        if self.is_photo:
            self.photo.source = no_photo
        else:
            self.photo.source = photo if photo else no_photo

        # toggle self.is_photo
        self.is_photo = not self.is_photo

    def confirm_adding(self, instance: Widget) -> None:
        """
        Save the information, photo and sound file to the database, redirect to
        [`AddVocab`](/reference/#front_ends.add_vocab.AddVocab) page, and show the result in a popup message box.

        Args:
             instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        # update database
        result = update_database(self.ti_word.text,
                                 self.ti_definition.text,
                                 self.ti_example.text,
                                 self.photo.source,
                                 sound=App.get_running_app().__getattribute__('add_vocab').sound)

        # go to slide
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('add_vocab')
        )

        # popup message
        msg = Popup(title='Message', size_hint=(None, None), size=(200, 100))
        if result:
            msg.content = Label(text="1 word added")
            msg.background_color = (0.4, 1.0, 0.3, 1.0)
            App.get_running_app().__getattribute__('add_vocab').update_words_added()
        else:
            msg.content = Label(text="0 word added")
            msg.background_color = (1.0, 0.4, 0.3, 1.0)

        msg.open()
        Clock.schedule_once(msg.dismiss, 1)
