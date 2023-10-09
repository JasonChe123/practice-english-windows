"""
`front_ends/database.py`\n
This module consists of `Database` which is a page let user amend the information of the vocabulary from the database.
"""

import pandas as pd
import os

from front_ends.cover_page import Popup
from front_ends.preview import Preview
from front_ends.select_photo import SelectPhoto
from library.logic.database import update_database

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class Database(Widget):
    """
    A page let user access database and amend the information.
    """
    id = 'database'

    def __init__(self):
        super(Database, self).__init__()
        self.vocabs = []
        self.count = 0

    def go_back(self) -> None:
        """
        Callback method from Go-Back Button. Redirect to [`CoverPage`](/reference/#front_ends.cover_page.CoverPage) and
        clear the data_table.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('cover_page')
        )
        self.ids['data_table'].clear_widgets()

    def init_data(self) -> None:
        """
        Extract all vocabulary from the database and show them to the data_table.
        """
        # reset search box
        self.ids['ti_search'].text = ''

        # verify existence of database
        file_path = os.path.join(App.get_running_app().working_dir, 'database', 'vocabulary.csv')
        if not os.path.isfile(file_path):
            return

        # read data
        data = pd.read_csv(file_path, index_col=0)

        # add vocabulary to the table
        self.ids['data_table'].cols = 1
        self.vocabs = data['Vocabulary'].tolist()
        self.vocabs.sort()
        self.show_data(self.vocabs)

        # show total vocab
        self.ids['total_vocab'].text = str(data.shape[0])

    def show_data(self, data: list):
        """
        Show the given data in the data_table.

        Args:
            data: A list of vocabulary.
        """
        self.ids['data_table'].clear_widgets()
        for vocab in data:
            button = Button(text=vocab, size=(300, 25), size_hint=(None, None), halign='left', valign='middle',
                            background_color=(0, 0, 0, 0))
            button.text_size = button.size
            button.bind(on_press=self.view_detail)
            self.ids['data_table'].add_widget(button)

    def view_detail(self, button: Button) -> None:
        """
        Callback method from buttons in `data_table`. Redirect to [`PreviewUpdate`](/reference/#front_ends.database.PreviewUpdate)
        page, and show the information for the vocabulary.

        Args:
            button: A button showing a vocabulary. It is given by the caller automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('preview_update')
        )
        App.get_running_app().__getattribute__('preview_update').vocab = button.text
        App.get_running_app().__getattribute__('preview_update').update_gui()

    def search_text(self, text: str) -> None:
        """
        Callback method from Search Box in Database page. It adds this event into the buffer first, if the user stop
        typing for 0.3 second, it will search vocabulary/ies containing the text from the database.

        Args:
            text: A string as a hint to find vocabulary from the database.
        """
        self.count += 1
        Clock.schedule_once(lambda t: self.update_count(text), 0.3)

    def update_count(self, text: str) -> None:
        """
        An event counter called by [`search_text`](/reference/#front_ends.database.Database.search_text), only find the
        vocabulary if the counter is equal to one.

        Args:
             text: A string as a hint to find vocabulary from the database.
        """
        if self.count == 1:
            filtered_list = [vocab for vocab in self.vocabs if text.lower() in vocab.lower().strip()]
            self.show_data(filtered_list)
            self.count -= 1
        else:
            self.count -= 1


class PreviewUpdate(Preview):
    """
    A page shows the information for the vocabulary, let user amends the information and update the database.
    """
    id = 'preview_update'

    def __init__(self):
        super(PreviewUpdate, self).__init__()
        self.working_dir = os.path.join(App.get_running_app().working_dir)
        self.vocab = ''
        self.ids['btn_confirm'].text = 'confirm update'

    def update_gui(self) -> None:
        """
        Show the information for the vocabulary from the database.
        """
        vocab_searching = self.vocab
        self.show_photo(Widget())
        self.set_sound()
        self.set_text_input(vocab_searching)

    def show_photo(self, instance: Widget = Widget()) -> None:
        """
        Show photo of the vocabulary from the database.
        """
        # data cleaning for self.vocab
        if '(' in self.vocab:
            self.vocab = self.vocab[:self.vocab.index('(')]
        self.vocab = self.vocab.strip().replace(' ', '_').lower()

        # fetch the photo from database
        vocab_image = os.path.join(self.working_dir, 'database', 'images', f'{self.vocab}.jpg')
        print(vocab_image)
        no_photo_image = os.path.join(self.working_dir, 'library', 'images', f'no_image.png')

        # declare photo source
        image = vocab_image if os.path.isfile(vocab_image) else no_photo_image

        # change photo
        self.photo.source = image
        self.photo.reload()

    def change_photo(self, instance: Widget = Widget()) -> None:
        self.search_photos()

    def search_photos(self):
        """
        Search photos from [`iStockPhoto`](https://www.istockphoto.com/) for word, definition and example.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('search_photos')
        )
        Clock.schedule_once(
            lambda t: App.get_running_app().__getattribute__('search_photos').
            get_photos(word=self.ti_word.text,
                       definition=self.ti_definition.text,
                       example=self.ti_example.text),
            0.6
        )

    def update_photo(self, url: str) -> None:
        """
        Update the photo from the given url.
        """
        self.photo.source = url

    def set_sound(self) -> None:
        """
        Fetch the sound file of the vocabulary from the database, and play it.
        """
        dimming_color = (0.3, 0.3, 0.3, 0.5)
        normal_color = (1.0, 1.0, 1.0, 1.0)
        sound_file = os.path.join(self.working_dir, 'database', 'sounds', f'{self.vocab}.mp3')
        if os.path.isfile(sound_file):
            color = normal_color
            player = SoundLoader.load(sound_file)
            player.play()
        else:
            color = dimming_color

        self.speaker.background_color = color

    def set_text_input(self, vocab_searching: str) -> None:
        """
        Fetch information from the database and show it.

        Args:
            vocab_searching: A text to search exactly the same value in the 'Vocabulary' column from the database.
        """
        # verify existence of database
        file_path = os.path.join(App.get_running_app().working_dir, 'database', 'vocabulary.csv')
        if not os.path.isfile(file_path):
            return

        # read data
        data = pd.read_csv(file_path, index_col=0)

        # extract information
        data = data[data['Vocabulary'].str[:] == vocab_searching].reset_index(drop=True).fillna('')
        if data.empty:
            return

        # set text
        self.ti_word.text = data['Vocabulary'][0]
        if data['Type'][0]:
            self.ti_word.text += f" ( {data['Type'][0]} )"
        self.ti_definition.text = data['Description'][0]
        self.ti_example.text = data['Example'][0]

    def go_back(self) -> None:
        """
        Callback method from Go-Back Button. Redirect to [`Database`](/reference/#front_ends.database.Database) page.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('database')
        )

    def confirm_adding(self, instance: Widget) -> None:
        self.confirm_update()

    def confirm_update(self) -> None:
        """
        Let user update word/ definition/ example or photo in the database. Redirect to
        [`Database`](/reference/#front_ends.database.Database) page.
        """

        result = update_database(self.ti_word.text,
                                 self.ti_definition.text,
                                 self.ti_example.text,
                                 self.photo.source,
                                 sound=None)

        # # go to slide
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('database')
        )

        # popup message
        msg = Popup(title='Message', size_hint=(None, None), size=(200, 100))
        msg.background_color = (0.4, 1.0, 0.3, 1.0) if result else (1.0, 0.4, 0.3, 1.0)
        msg.content = Label(text="update success") if result else Label(text="update failed")
        msg.open()
        Clock.schedule_once(msg.dismiss, 1)


class SearchPhoto(SelectPhoto):
    """
    Search photos from [`iStockPhoto`](https://www.istockphoto.com/).
    """
    id = 'search_photos'

    def __init__(self):
        super(SearchPhoto, self).__init__()

    def go_back(self) -> None:
        """
        Callback method from Go-Back Button. Redirect to [`PreviewUpdate`](/reference/#front_ends.database.PreviewUpdate)
        page.

        Arg:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('preview_update')
        )
        self.reset_photos()

    def add_photo(self, instance: Widget = Widget()) -> None:
        """
        Change the photo of and redirect to [`PreviewUpdate`](/reference/#front_ends.database.PreviewUpdate) page.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('preview_update')
        )
        App.get_running_app().__getattribute__('preview_update').update_photo(instance.source)
        self.reset_photos()
