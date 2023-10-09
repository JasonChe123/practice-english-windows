from kivy.app import App
from kivy.uix.widget import Widget


class OnlineTesting(Widget):
    def __init__(self):
        super().__init__()

    def go_back(self):
        """
        Callback method from Go-Back Button. Redirect to [`CoverPage`](/reference/#front_ends.cover_page.CoverPage) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('cover_page')
        )