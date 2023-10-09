"""
`search_photos.py`\n
This module consists of IStockPhoto which crawl photos from [`iStockPhoto`](https://www.istockphoto.com/).
"""

from bs4 import BeautifulSoup as bs
import requests
import requests.utils


class IStockPhoto:
    """
    This class search the photos according to the given words from [`iStockPhoto`](https://www.istockphoto.com/) and
    return a list of the photos' link.
    """
    def __init__(self):
        self.header = requests.utils.default_headers()
        self.header.update({'User-Agent': 'Jason'})
        self.photo_src = []

    def search_photos(self, url: str = '') -> list:
        """
        Search photo according to the given url. Return a list of links of the photos.

        Args:
            url: A url of a searched word in iStockPhoto.

        Returns:
            A list of links of the photos from search result.
        """
        html = self._request_content(url)
        self.photo_src = []
        if html:
            soup = bs(html, 'html.parser')
            photos = soup.find_all('img')
            for i in photos:
                source_link = i['src']
                if source_link.startswith('https://'):
                    self.photo_src.append(source_link)

        return self.photo_src

    def _request_content(self, url):
        try:
            res = requests.get(url, headers=self.header)
            return res.content
        except Exception as e:
            print(f"Exception from iStockPhoto._request_content:\n\t{e}")
            return
