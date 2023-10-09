"""
`front_ends/practice_vocab.py`\n
This module consists of `PracticeVocab` which allow user to practice vocabulary from the database.
"""

import pandas as pd
import os
import time
from library.logic.database import get_data
from library.logic.database import get_sound
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget


class PracticeVocab(Widget):
    """
    A page let user practices vocabulary from the database, and counts number of correct answer.
    """
    id = 'practice_vocab'
    image = ObjectProperty(None)
    lbl_def = ObjectProperty(None)
    lbl_ex = ObjectProperty(None)
    lbl_words_tested = ObjectProperty(None)
    lbl_words_correct = ObjectProperty(None)
    lbl_percent_correct = ObjectProperty(None)
    ti_answer = ObjectProperty(None)

    def __init__(self):
        super(PracticeVocab, self).__init__()
        self.practice_num = 0
        self.practice_method = 'all'
        self.data = None
        self.testing_word = None
        self.tested = 0
        self.correct = 0

    def go_back(self) -> None:
        """
        Callback method from Go-Back Button. Redirect to [`CoverPage`](/reference/#front_ends.cover_page.CoverPage)
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('cover_page')
        )

    def start_practice(self) -> None:
        """Get information from the database and count number of correct answer."""
        # self.practice_num and self.practice_method are decided by cover_page popup
        self.data = get_data(self.practice_num, self.practice_method)

        # reset params
        self.tested = 0
        self.correct = 0
        self.testing_word = None
        self.ti_answer.text = ''
        if not isinstance(self.data, pd.DataFrame):
            return

        # update statistic
        self.lbl_words_tested.text = f"{self.tested} words tested"
        self.lbl_words_correct.text = f"{self.correct} words correct"
        self.lbl_percent_correct.text = "0% correct"

        # start testing
        self.next_word()

    def next_word(self, instance='') -> None:
        """
        Get a word/ phrase from the testing dataset and show the information in the user interface.

        Args:
             instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.ti_answer.disabled = False
        self.ti_answer.focus = True
        self.ti_answer.select_all()
        word = self.get_word()
        if isinstance(word, pd.DataFrame):
            self.refresh_gui(word)

    def get_word(self) -> pd.DataFrame | None:
        """
        Return a row of data(Dataframe) from a testing dataset. Return None if the testing data is finished.

        Returns:
            A row of data in DataFrame format, including word, description, example, etc.
        """
        if len(self.data) == 0:
            print('no word to test')
            return

        # get word
        self.testing_word = self.data.tail(1).reset_index()
        self.data.drop(self.data.tail(1).index, inplace=True)

        return self.testing_word

    def refresh_gui(self, word: pd.DataFrame) -> None:
        """
        Update the user interface according to the information of 'word' and the image file from the database.

        Args:
            word: A row of DataFrame includes description, examples, etc. of the word/ phrase.
        """
        vocab = word['Vocabulary'][0]

        # set image
        if '(' in vocab:
            vocab_raw = vocab[:vocab.find('(')].strip()
        else:
            vocab_raw = vocab
        file_name = vocab_raw.replace(' ', '_').lower()
        image_1 = f'{App.get_running_app().working_dir}/database/images/{file_name}.png'
        image_2 = f'{App.get_running_app().working_dir}/database/images/{file_name}.jpeg'
        image_3 = f'{App.get_running_app().working_dir}/database/images/{file_name}.jpg'
        if os.path.isfile(image_1):
            self.image.source = image_1
        elif os.path.isfile(image_2):
            self.image.source = image_2
        elif os.path.isfile(image_3):
            self.image.source = image_3
        else:
            self.image.source = f'{App.get_running_app().working_dir}/library/images/no_image.png'

        # set definition and example
        word_type = vocab[vocab.find('('):vocab.find(')')+1]
        mask = "*" * len(vocab_raw)
        self.lbl_def.text = f"{word_type} {word['Description'][0]}"
        self.lbl_ex.text = word['Example'][0].replace(vocab_raw, mask)

    def check_answer(self, instance):
        """
        Check the answer provided by the user. Update the marks(correct answer) and get next word to test.

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        if self.tested == self.practice_num:
            return

        self.ti_answer.disabled = True
        self.ti_answer.select_all()

        # define answer
        vocab = self.testing_word['Vocabulary'][0].lower().strip()
        if '(' in vocab:
            ans = vocab[:vocab.find('(')].strip()
        else:
            ans = vocab

        # check answer
        self.tested += 1
        msg = Popup(title='Answer', size_hint=(0.7, None), size=(0, 150), auto_dismiss=False)
        if instance.text.lower().strip() == ans:
            self.correct += 1
            msg.content = Label(text=f"({instance.text}) Correct")
            msg.background_color = (0.2, 1.0, 0.2, 1.0)
            t = 1
        else:
            msg.content = Label(text=ans)
            msg.background_color = (1.0, 0.2, 0.2, 1.0)
            t = 3
        msg.open()
        Clock.schedule_once(msg.dismiss, t)

        # play sound
        sound = get_sound(ans.replace(' ', '_'))
        if sound:
            Clock.schedule_once(lambda t: SoundLoader.load(sound).play(), 0)
        Clock.schedule_once(self.next_word, t)

        # update statistic
        self.lbl_words_tested.text = f"{self.tested} words tested"
        self.lbl_words_correct.text = f"{self.correct} words correct"
        self.lbl_percent_correct.text = f"{int(self.correct/self.tested*100)}% correct"
