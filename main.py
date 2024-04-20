from kivy.config import Config
Config.set('graphics', 'resizable', False)
import os
from front_ends.cover_page import CoverPage
from front_ends.add_vocab import AddVocab
from front_ends.database import Database
from front_ends.learn_grammar import LearnGrammar
from front_ends.online_testing import OnlineTesting
from front_ends.practice_listening import PracticeListening
from front_ends.practice_vocab import PracticeVocab
from front_ends.preview import Preview
from front_ends.read_news import ReadNews
from front_ends.select_photo import SelectPhoto
from front_ends.database import PreviewUpdate, SearchPhoto
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.carousel import Carousel


# load kv files
project_dir = os.path.dirname(os.path.abspath(__file__))
kv_dir = os.path.join(project_dir, 'front_ends', 'kv_files')
kv_files = os.listdir(kv_dir)
kv_files.remove('sample_widget.kv')
Builder.load_file(os.path.join(kv_dir, 'sample_widget.kv'))
[Builder.load_file(os.path.join(kv_dir, kv)) for kv in kv_files]


class PracticeEnglishApp(App):
    working_dir = project_dir

    def build(self):
        Window.size = (450, 800)
        self.main_container = Carousel(direction='right', scroll_timeout=0)

        # assign attributes and add widgets as kv_files name
        self.cover_page = CoverPage()
        self.add_vocab = AddVocab()
        self.database = Database()
        self.learn_grammar = LearnGrammar()
        self.online_testing = OnlineTesting()
        self.practice_listening = PracticeListening()
        self.practice_vocab = PracticeVocab()
        self.preview = Preview()
        self.read_news = ReadNews()
        self.select_photo = SelectPhoto()

        self.main_container.add_widget(self.cover_page)
        self.main_container.add_widget(self.add_vocab)
        self.main_container.add_widget(self.database)
        self.main_container.add_widget(self.learn_grammar)
        self.main_container.add_widget(self.online_testing)
        self.main_container.add_widget(self.practice_listening)
        self.main_container.add_widget(self.practice_vocab)
        self.main_container.add_widget(self.preview)
        self.main_container.add_widget(self.read_news)
        self.main_container.add_widget(self.select_photo)

        # these classes are inherited from another classes and aren't belong to any kv file
        self.preview_update = PreviewUpdate()
        self.search_photos = SearchPhoto()
        self.main_container.add_widget(self.preview_update)
        self.main_container.add_widget(self.search_photos)

        return self.main_container


if __name__ == '__main__':
    PracticeEnglishApp().run()
