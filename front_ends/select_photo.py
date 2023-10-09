"""
`front_ends/select_photo.py`
\nThis module consists of `SelectPhoto` which allows user to select a photo as a hint to remember the vocabulary.
"""

import math
import os
import time

from library.logic.search_photos import IStockPhoto
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty


class SelectPhoto(Widget):
    """
    A page let user select the desire photo for the vocabulary.
    """

    id = 'select_photo'
    photo_1 = ObjectProperty(None)
    photo_2 = ObjectProperty(None)

    def __init__(self):
        super(SelectPhoto, self).__init__()
        self.page_index = 0
        self.photos = []
        self.photo_to_be_added = ''
        self.istock_photo = IStockPhoto()
        self.reset_photos()

    def go_back(self) -> None:
        """
        Callback button from Go-Back Button. Redirect to [`AddVocab`](/reference/#front_ends.add_vocab.AddVocab) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('add_vocab')
        )
        self.reset_photos()

    def get_photos(self, word: str, definition: str, example: str) -> None:
        """
        Search photos from the [`iStockPhoto`](https://www.istockphoto.com) and show it in the user interface. It
        searches the word first, then the definition and search the example.

        Args:
            word: The vocabulary.
            definition: The definition of the vocabulary.
            example: The example of the vocabulary.
        """
        url = r'https://www.istockphoto.com/search/2/image?phrase='
        self.photos = []
        for t in (word, definition, example):
            self.photos += self.istock_photo.search_photos(url + t)

        self.show_photos()

    def show_photos(self) -> None:
        """Show the photos in the user interface."""
        if not self.photos:
            return

        # define photos
        photo1 = self.page_index*2
        photo2 = self.page_index*2 + 1
        no_image = os.path.join(App.get_running_app().working_dir, 'library', 'images', 'no_image.png')

        # set photo source
        self.photo_1.source = self.photos[photo1]
        self.photo_2.source = self.photos[photo2] if photo2 < len(self.photos) else no_image

    def previous_photos(self, instance: Widget) -> None:
        """
        Show the previous 2 photos from the crawling result.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.page_index = max(self.page_index - 1, 0)
        self.show_photos()

    def next_photos(self, instance: Widget) -> None:
        """
        Show the next 2 photos from the crawling result.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.page_index = min(math.ceil(len(self.photos)/2)-1, self.page_index + 1)
        self.show_photos()

    def add_photo(self, instance: Widget) -> None:
        """
        Add the selected photo to the 'to_be_added' attribute, and redirect to
        [`AddVocab`](/reference/#front_ends.add_vocab.AddVocab) page.

        Args:
             instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.photo_to_be_added = instance.source
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('add_vocab')
        )
        self.reset_photos()

    def reset_photos(self) -> None:
        """Reset the photos to 'loading' image."""
        self.page_index = 0
        self.photos = []
        loading_image = os.path.join(App.get_running_app().working_dir, 'library', 'images', 'loading.gif')
        self.photo_1.source = loading_image
        self.photo_2.source = loading_image
