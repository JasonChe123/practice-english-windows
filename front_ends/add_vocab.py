"""
`front_ends.add_vocab.py`\n
This module consists of a `AddVocab` which allow user to find definition, examples, sound and photos of the text and
save it to the database. The information is mainly crawled from [Cambridge Online Dictionary](https://dictionary.cambridge.org/)
and [iStockPhoto](https://www.istockphoto.com/).
"""

import os
import requests
import webbrowser
from library.logic.online_dictionary import CambridgeDictionary
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget


class AddVocab(Widget):
    """
    A page let user adds vocabulary to the database. The definitions, examples, sounds and photos are crawled from
    the internet, but the user can still manually type the words, definition or examples rather than using online
    resources.
    """

    id = 'add_vocab'

    lbl_word = ObjectProperty(None)
    lbl_word_tenses = ObjectProperty(None)
    lbl_word_func = ObjectProperty(None)
    lbl_word_added = ObjectProperty(None)

    ti_def = ObjectProperty(None)
    ti_example = ObjectProperty(None)
    ti_search = ObjectProperty(None)
    ti_translation = ObjectProperty(None)

    btn_def_next = ObjectProperty(None)
    btn_def_prev = ObjectProperty(None)
    btn_speaker = ObjectProperty(None)
    btn_usage_prev = ObjectProperty(None)
    btn_usage_next = ObjectProperty(None)
    btn_exp_next = ObjectProperty(None)
    btn_exp_prev = ObjectProperty(None)

    cambridge = CambridgeDictionary()

    def __init__(self, region='uk'):
        super(AddVocab, self).__init__()
        self.region = region
        self.sound = None
        self.words_added = 0

        # dictionary
        self.dict = []
        self.meaning = []
        self.curr_usage = {}
        self.gen_info = []

        # indexes
        self.def_index = 0
        self.usage_index = 0
        self.example_index = 0

        self.set_button_color()

    def processing_dictionary(self, result: dict, translation: str, sound: str | requests.models.Response) -> None:
        """
        Shows data in the user interface.

        Args:
            result: A dictionary contains word function, definition, examples, etc.
            translation: A Chinese translation of the text.
            sound: An empty string (no sound has been found) or a requests' response (contain bytes code of a .mp3 file).
        """

        self.clear_gui()
        self.sound = None
        App.get_running_app().__getattribute__('select_photo').photo_to_be_added = ''
        if result:
            self.dict = result[self.region]
            if not self.dict:
                return
            self.sound = sound
            self.save_sound_file()
            self.refresh_gui()
            self.ti_translation.text = translation
            self.set_button_color()
        else:
            self.ti_def.text = f"no response/ result from Cambridge Online Dictionary."
            self.dict = []
            self.meaning = []
            self.curr_usage = {}
            self.gen_info = []
            self.def_index = 0
            self.usage_index = 0
            self.example_index = 0
            self.set_button_color()

    def clear_gui(self) -> None:
        """Reset the text inputs and labels in `AddVocab` to empty string."""
        # reset indexes
        self.def_index = 0
        self.usage_index = 0
        self.example_index = 0

        # clear content
        for lbl in (self.lbl_word, self.lbl_word_func, self.lbl_word_tenses, self.ti_def, self.ti_example, self.ti_translation):
            lbl.text = ""

    def refresh_gui(self) -> None:
        """Update user interface(definition, examples, etc.)"""
        self.gen_info, self.meaning = self.unpack_dictionary()
        self.curr_usage = self.meaning[self.usage_index]

        # update gui
        self.update_definition()
        self.update_usage()
        self.update_explanation()
        self.update_example()

    def unpack_dictionary(self) -> (list, list):
        """
        Unpack the information.

        Returns:
             A list of general information of the text and a list of definition and examples of the text.
        """
        block = self.dict[self.def_index]
        return block['gen_info'], block['meanings']

    def set_button_color(self) -> None:
        """Set 'next buttons' and 'previous buttons' color to show its validity."""
        dimming_color = (0.3, 0.3, 0.3, 0.5)
        normal_color = (1.0, 1.0, 1.0, 1.0)

        for instance in (self.btn_def_prev, self.btn_def_next, self.btn_speaker,
                         self.btn_usage_prev, self.btn_usage_next,
                         self.btn_exp_prev, self.btn_exp_next):
            color = normal_color

            # definition buttons
            if instance == self.btn_def_prev:
                if self.def_index == 0:
                    color = dimming_color
            elif instance == self.btn_def_next:
                if not self.dict or self.def_index == len(self.dict) - 1:
                    color = dimming_color

            # speaker button
            elif instance == self.btn_speaker:
                if not self.sound:
                    color = dimming_color

            # usage buttons
            elif instance == self.btn_usage_prev:
                if self.usage_index == 0:
                    color = dimming_color
            elif instance == self.btn_usage_next:
                if not self.meaning or self.usage_index == len(self.meaning) - 1:
                    color = dimming_color

            # example buttons
            elif instance == self.btn_exp_prev:
                if self.example_index == 0:
                    color = dimming_color
            elif instance == self.btn_exp_next:
                if not self.curr_usage or self.example_index == len(self.curr_usage['definitions'][0]['examples']) - 1:
                    color = dimming_color

            instance.background_color = color

    def update_definition(self) -> None:
        """Update definition label `lbl_word` and `lbl_word_tenses`."""
        self.lbl_word.text = f"   {self.gen_info[0]}   ( {self.gen_info[1]} )"
        self.lbl_word_tenses.text = f"      {self.gen_info[4].replace('present participle', '').replace('past tense', '').replace('past participle', '')}"

    def update_usage(self) -> None:
        """Update the word function label `lbl_word_func`."""
        if self.curr_usage['definitions'][0]['level']:
            level = f"< {self.curr_usage['definitions'][0]['level']} >"
        else:
            level = ""
        self.lbl_word_func.text = f"      {self.curr_usage['word_function']}   {level}"

    def update_explanation(self) -> None:
        """Update the definition text-input `ti_def`."""
        self.ti_def.text = self.curr_usage['definitions'][0]['explanation']  # only display the first definition

    def update_example(self) -> None:
        """Update the example text-input `ti_example`."""
        self.ti_example.text = self.curr_usage['definitions'][0]['examples'][self.example_index]

    def save_sound_file(self) -> None:
        """Save the sound file to temp.mp3 for later use."""
        file = os.path.join(App.get_running_app().working_dir, 'library', 'sounds', 'temp.mp3')
        if self.sound:
            with open(file, 'wb') as f:
                f.write(self.sound.content)

    # --- 4 main buttons' callback ---
    def check_dictionary(self, instance: Widget) -> None:
        """
        Callback method from text-input `ti_search` or Dictionary IconButton. Call [`check`](/reference/#library.logic.online_dictionary.CambridgeDictionary.check)
        to search the definition from [Cambridge Online Dictionary](https://dictionary.cambridge.org/); call
        [`processing_dictionary`](/reference/#front_ends.add_vocab.AddVocab.processing_dictionary) to process the data
        and show it in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.ti_search.select_all()
        res, translation, sound = self.cambridge.check(self.ti_search.text)
        self.processing_dictionary(res, translation, sound)

    def add_images(self, instance: Widget) -> None:
        """
        Callback method from Photo Button. Crawl photos from [iStockPhoto](https://www.istockphoto.com/) and show it in
        the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('select_photo')
        )
        msg = Popup(title='Message', size_hint=(0.7, None), size=(0, 150), content=Label(text='Loading...'), auto_dismiss=False)
        msg.open()
        Clock.schedule_once(msg.dismiss, 2)
        Clock.schedule_once(
            lambda w: App.get_running_app().
            __getattribute__('select_photo').
            get_photos(
                self.ti_search.text,
                self.ti_def.text,
                self.ti_example.text
            ),
            1.0)

    def google_search(self) -> None:
        """
        Callback method from Search Button. It opens a browser and google search it.
        """
        text = self.ids['text_input_search'].text
        webbrowser.open(f'https://www.google.com/search?q={text.replace(" ", "+")}')

    def update_database(self, instance: Widget) -> None:
        """
        Callback method from Add Word Button. It displays the information and ready to save to the database.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('preview')
        )
        App.get_running_app().__getattribute__('preview').refresh_gui()

    def update_words_added(self) -> None:
        """It shows the number of words added in this session."""
        self.words_added += 1
        if self.words_added > 1:
            self.lbl_word_added.text = f"{self.words_added} words added"
        else:
            self.lbl_word_added.text = f"{self.words_added} word added"

    # --- other buttons' callback ---
    def go_back(self) -> None:
        """
        Callback method from Go-Back Button. Redirect to the [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('cover_page')
        )

    def definition_previous(self, instance: Widget) -> None:
        """
        Callback method from Button `btn_def_prev`. Get the previous definition and show it in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        if not self.dict:
            return

        # extract data
        self.def_index = max(0, self.def_index - 1)
        self.gen_info, self.meaning = self.unpack_dictionary()

        # update gui
        self.update_definition()
        self.set_button_color()

        # reset word_fuction, explanation and example
        self.usage_index = 0
        self.example_index = 0
        self.usage_previous('foo')
        self.example_previous('foo')

    def definition_next(self, instance: Widget) -> None:
        """
        Callback method from Button `btn_def_next`. Get the next definition and show it in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        if not self.dict:
            return

        # extract data
        self.def_index = min(len(self.dict) - 1, self.def_index + 1)
        self.gen_info, self.meaning = self.unpack_dictionary()

        # update gui
        self.update_definition()
        self.set_button_color()

        # reset word_fuction, explanation and example
        self.usage_index = 0
        self.example_index = 0
        self.usage_previous('foo')
        self.example_previous('foo')

    def usage_previous(self, instance: Widget) -> None:
        """
        Callback method from `btn_usage_prev`. Get the previous definition and show it in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        if not self.meaning:
            return

        # extract data
        self.usage_index = max(0, self.usage_index - 1)
        self.curr_usage = self.meaning[self.usage_index]

        # update gui
        self.update_usage()
        self.update_explanation()
        self.set_button_color()

        # reset example
        self.example_index = 0
        self.example_previous('foo')

    def usage_next(self, instance: Widget) -> None:
        """
        Callback method from `btn_usage_next`. Get the next definition and show it in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        if not self.meaning:
            return

        # extract data
        self.usage_index = min(len(self.meaning) - 1, self.usage_index + 1)
        self.curr_usage = self.meaning[self.usage_index]

        # update gui
        self.update_usage()
        self.update_explanation()
        self.set_button_color()

        # reset example
        self.example_index = 0
        self.example_previous('foo')

    def example_previous(self, instance: Widget) -> None:
        """
        Callback method from `btn_exp_prev`. Get the previous example and show it in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        if not self.curr_usage:
            return

        self.example_index = max(0, self.example_index - 1)
        self.update_example()
        self.set_button_color()

    def example_next(self, instance: Widget) -> None:
        """
        Callback method from `btn_exp_next`. Get the next example and show it in the user interface.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        if not self.curr_usage:
            return

        self.example_index = min(len(self.curr_usage['definitions'][0]['examples']) - 1, self.example_index + 1)
        self.update_example()
        self.set_button_color()

    def play_sound(self, instance: Widget) -> None:
        """Callback method from Button `button_speaker`. Play the temporary mp3 file.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        file = os.path.join(App.get_running_app().working_dir, 'library', 'sounds', 'temp.mp3')
        SoundLoader.load(file).play()
