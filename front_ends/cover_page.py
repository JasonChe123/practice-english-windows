"""
`front_ends.cover_page.py`\n
This module consists of:
    - `CoverPage` which directs user to difference pages
    - `PopupQuestion` and `PopupQuestionDatabase` which let user picks choices
"""

import threading as th
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget


class CoverPage(Widget):
    """A main page contains 8 main buttons: **Add Vocabulary**, **Practice Vocabulary**, **Learn Grammar**,
    **Read News**, **Video Learning**, **Online Testing** and **Database**. (Structure of the user interface can be
    found in folder `front_ends/kv_files`)"""

    id = 'cover_page'

    def __init__(self):
        super(CoverPage, self).__init__()

    def go_to_add_vocab(self, instance: Widget) -> None:
        """
        Callback method from Add Vocabulary Button in [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        Redirect to [`AddVocab`](/reference/#front_ends.add_vocab.AddVocab).

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('add_vocab')
        )

    def go_to_practice_vocab(self, instance: Widget) -> None:
        """
        Callback method from Practice Vocabulary Button in [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        Redirect to [`PracticeVocab`](/reference/#front_ends.practice_vocab.PracticeVocab) and call
        [`PopupQuestion`](/reference/#front_ends.cover_page.PopupQuestion).

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('practice_vocab')
        )
        PopupQuestionNumberOfWords().open()

    def go_to_database(self) -> None:
        """
        Callback method from Database Button in [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        Redirect to[`Database`](/reference/#front_ends.database/Database).
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('database')
        )
        Clock.schedule_once(
            lambda t: App.get_running_app().__getattribute__('database').init_data(),
            0.6
        )

    def go_to_read_news(self) -> None:
        """
        Callback method from Read News Button in [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        Redirect to [`ReadNews`](/reference/#front_ends.read_news.ReadNews) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('read_news')
        )

    def go_to_learn_grammar(self) -> None:
        """
        Callback method from Learn Grammar Button in [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        Redirect to [`LearnGrammar`](/reference/#front_ends.read_news.LearnGrammar) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('learn_grammar')
        )

    def go_to_practice_listening(self) -> None:
        """
        Callback method from Learn Practice Listening Button in [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        Redirect to [`PracticeListening`](/reference/#front_ends.practice_listening.PracticeListening) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('practice_listening')
        )

    def go_to_online_testing(self) -> None:
        """
        Callback method from Online Testing Button in [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).
        Redirect to [`OnlineTesting`](/reference/#front_ends.online_testing.OnlineTesting) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('online_testing')
        )


class PopupQuestionNumberOfWords(Popup):
    """A popup window which ask user to select number of vocabulary to be practiced."""

    def go_back(self, instance: Widget) -> None:
        """
        Callback method from Cancel Button. Redirect to [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.dismiss()
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('cover_page')
        )

    def get_number(self, number: int) -> None:
        """
        Callback method from Number Button (30/ 50/ 100). To set value of
        `front_ends.practice_vocab.PracticeVocab.practice_num` and call
        [`PopupQuestionPracticeMethod`](/reference/#front_ends.cover_page.PopupQuestionPracticeMethod).

        Args:
            number: A number selected by user through the popup window.
        """
        App.get_running_app().__getattribute__('practice_vocab').practice_num = number
        self.dismiss()
        PopupQuestionPracticeMethod().open()


class PopupQuestionPracticeMethod(Popup):
    """A popup window which ask user to select practice method (latest words/ random words from the database)."""

    def go_back(self, instance: Widget) -> None:
        """
        Callback method from Cancel Button. Redirect to [`CoverPage`](/reference/#front_ends.cover_page.CoverPage).

        Args:
            instance: This is a kivy's widget. This argument will be passed from a caller widget automatically.
        """
        self.dismiss()
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('cover_page')
        )

    def get_method(self, method: str) -> None:
        """
        Callback method from Rounded Button (The latest words/ All words). Set value of
        `front_ends.practice_vocab.PracticeVocab.practice_method` and call
        [`start_practice`](/reference/#front_ends.practice_vocab.PracticeVocab.start_practice).

        Args:
            method: Define how to get words to practice, random words or the latest words from the database.
                    Receive 'all' or 'latest' from button's callback.
        """
        App.get_running_app().__getattribute__('practice_vocab').practice_method = method
        self.dismiss()
        App.get_running_app().__getattribute__('practice_vocab').start_practice()
