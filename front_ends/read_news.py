"""
`front_ends/read_news.py`\n
This module consists of `ReadNews` which show the hyperlink for reading news.
"""

from kivy.app import App
from kivy.uix.widget import Widget


class ReadNews(Widget):
    """
    A page shows some useful links for reading news. It will open a browser and go to the specified website.
    """
    def __init__(self):
        super().__init__()

    def go_back(self) -> None:
        """
        Callback method from Go-Back Button. Redirect to [`CoverPage`](/reference/#front_ends.cover_page.CoverPage) page.
        """
        App.get_running_app().main_container.load_slide(
            App.get_running_app().__getattribute__('cover_page')
        )
