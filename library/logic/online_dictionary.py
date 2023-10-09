"""
`library.logic.online_dictionary.py`\n
This module consists of `CambridgeDictionary` which crawl data from [`Cambridge Online Dictionary`](https://dictionary.cambridge.org/)
"""

import re
import requests
import requests.utils
from bs4 import BeautifulSoup as bs
from bs4.element import Tag


class CambridgeDictionary:
    """This class handles the web crawling from [Cambridge Online Dictionary](https://dictionary.cambridge.org/). It copies
    the definitions and examples and download the pronunciation."""

    def __init__(self):
        self.res = {}
        self.translation = ''
        self.sound_link_respone = ''

    def check(self, word: str) -> (dict, str, str | requests.models.Response):
        """
        Callback method from [`check_dictionary`](/reference/#front_ends.add_vocab.AddVocab.check_dictionary).
        Check dictionary from Cambridge and return cleaned data.

        Args:
            word: Text from `ti_search` in [`AddVocab`](/reference/#front_ends.add_vocab.AddVocab).

        Returns:
            Dictionary contains information of the text; A chinese translation of the text; An empty string or requests'
                response contains bytes code of .mp3 file.
        """
        self._check_dictionary_from_web(word)

        return self.res, self.translation, self.sound_link_respone

    def _check_dictionary_from_web(self, word: str) -> None:
        """Callback method from `self.check`. Set value of `self.sound_link_response`, `self.res` and `self.translation`.

        Args:
            word: Text to be searched from [Cambridge Dictionary](https://dictionary.cambridge.org/).

        Returns:
            None

        """
        html = self._request_content(word)
        self.sound_link_respone = ''
        if html:
            soup = bs(html, 'html.parser')
            main_page = soup.find('article', {'id': 'page-content'})
            if main_page:
                page = main_page.find('div', {'class': 'page'})
                if page:
                    self.res = self._crawling(page)
                else:
                    print("page not found")

                # find pronunciation
                uk_voice = page.find('div', {'title': 'Listen to the British English pronunciation'})
                if uk_voice:
                    speaker = uk_voice.findPreviousSibling('audio', {'id': 'audio1'})
                    if speaker:
                        audio = speaker.findChild('source', {'type': 'audio/mpeg'})
                        link = 'https://dictionary.cambridge.org' + audio['src']
                        self.sound_link_respone = requests.get(link, headers=self.header)

                # find translation
                self.translation = ''
                translation = main_page.findChild('div', {'class': 'lmb-10'})
                if translation:
                    languages = translation.findChildren('div', {'class': 'pr bw lp-10 lmt-5'})
                    for lang in languages:
                        text = lang.findChild('div', {'class': 'tc-bd fs14 lmb-10'})
                        if text:
                            if 'in Chinese (Traditional)' in text.text:
                                trans = lang.findChild('div', {'class': 'tc-bb tb lpb-25 break-cj'})
                                self.translation = trans.text.replace('\n', '').replace(',', '，').replace('  ', ' ').replace(' ', '')
                                break
            else:
                print("main page not found, please search for another word")
                self.res = {}
                return
        else:
            print("cannot get html")
            self.res = {}
            return

    def _request_content(self, words: str) -> bytes | None:
        """Callback method from `self._check_dictionary_from_web`

        Args:
            words: Text to be searched from [Cambridge Dictionary](https://dictionary.cambridge.org/).

        Returns:
            Page content from [Cambridge Dictionary](https://dictionary.cambridge.org/), return None if error occur.
        """
        word = words.strip().replace(' ', '-')
        url = fr'https://dictionary.cambridge.org/dictionary/english/{word}'
        self.header = requests.utils.default_headers()
        self.header.update({'User-Agent': 'Jason'})
        try:
            res = requests.get(url, headers=self.header)
        except Exception as e:
            print(f"Exception from CambridgeDictionary._request_content:\n\t{e}")
            return

        return res.content

    def _crawling(self, page: Tag) -> dict:
        """Callback from `self._check_dictionary_from_web`. Data cleaning.

        Args:
            page: Tag of html.

        Returns:
            `dict` consists of important information regarding the text.
        """
        dictionary = {
            'uk': [],
            'us': [],
            'business_english': [],
        }

        # find dictionary region
        regions = page.findChildren('div', {'class': 'pr dictionary'})
        if regions:  # UK, US, BUSINESS ENGLISH
            for region in regions:
                dict_region = region.find('h2', {'class': 'c_hh'})

                # uk dictionary
                if not dict_region:
                    dictionary['uk'] = self._gather_info(region)

                # us dictionary
                elif 'American Dictionary' in dict_region.text:
                    dictionary['us'] = self._gather_info(region)

                # business english
                elif 'Business English' in dict_region.text:
                    dictionary['business_english'] = self._gather_info(region)

                # any other region
                else:
                    print(f"there is another dictionary region: {dict_region.text}")
            return dictionary
        else:
            print("dictionary regions not found")
            return dictionary

    def _gather_info(self, region: Tag) -> list:
        """Callback method from `self._crawling`. To gather information into the following format.\n
        res = [entry_blocks, ...]\n
        entry_blocks = {  # ('div', 'class': '*entry-body__el')
            'gen_info': {'word': '', 'form': '', 'uk_voice': '', 'us_voice': '', 'supp_info': '''},  # ('div', 'class': 'pos-header dpos-h')
            'meanings': [meaning_block, ...],
            }\n
        meaning_block = [  # ('div', 'class': 'pr dsense*')
            {'word_function': '',  # ('h3': 'class': 'dsense_h')
             'definitions': [def_block, ...]}, ...
         ]\n
        def_block = {  # ('div', 'class': 'def-block ddef_block ')
            'level': '',
            'explanation': '',
            'examples': [...],
        }\n
        idioms_block = []  # ('div': 'class': 'idiom-block')

        Args:
            region: Different region of english, e.g. US, UK.

        Returns:
            A list consists of important information of the text, e.g. definition, examples, etc.
        """
        res = []

        entry_blocks = region.find_all('div', {'class': re.compile('.*entry-body__el')})
        for entry in entry_blocks:
            gen_info = self._get_general_info(entry)
            meanings = []
            meaning_blocks = entry.find_all('div', {'class': re.compile('pr dsense.*')})
            for meaning in meaning_blocks:
                word_function = self._get_word_function(meaning)
                definitions = []
                meaning_block = {'word_function': word_function,
                                 'definitions': []}
                definition_blocks = meaning.find_all('div', {'class': 'def-block ddef_block'})
                for definition in definition_blocks:
                    level = self._get_word_levl(definition)
                    explanation = self._get_explanation(definition)
                    examples = self._get_example(definition)
                    definitions.append(
                        {'level': level,
                         'explanation': explanation,
                         'examples': examples}
                    )
                meaning_block['definitions'] = definitions
                meanings.append(meaning_block)

            res.append(
                {'gen_info': gen_info,
                 'meanings': meanings}
            )

        return res

    def _get_general_info(self, page: Tag) -> list:
        """Callback method from `_gather_info`. It gets general information (word form, word level, etc.)
        according to the specific Tag from the page content.

        Args:
            page: A page content from the website.

        Returns:
            A list consists of general information (word form, word level, etc.) of the text.
        """
        title = page.find('div', {'class': 'di-title'})
        word = title.find('h2')
        if not word:
            word = title.find('span', {'class': 'hw dhw'})
        form = page.find('span', {'class': 'pos dpos'})
        voice_uk = None
        voice_us = None
        tenses = page.find('span', {'class': 'irreg-infls dinfls'})
        res = []
        for i in (word, form, voice_uk, voice_us, tenses):
            i = i.text if i else ''
            res.append(i)

        return res

    def _get_word_function(self, page: Tag) -> str:
        """Callback method from `_gather_info`. It gets functions of the word(e.g. get: verb (obtain/ reach/ become...).

        Args:
            page: A page content from the website.

        Returns:
            Functions of the word.
        """
        word_function = page.find('h3', {'class': 'dsense_h'})
        if word_function:
            return word_function.text.replace('\n', '').replace('  ', '')

        return ''

    def _get_word_levl(self, page: Tag) -> str:
        """Callback method from `self._gather_info`. It gets the level(A1/ A2/ B1...) of the text.

        Args:
            page: A page content from the website.

        Returns:
            Level of the text(A1/ A2/ B1...).
        """
        regex = re.compile('epp-xref.*')
        level = page.findChild('span', {'class': regex})
        if level:
            return level.text
        return ''

    def _get_explanation(self, page: Tag) -> str:
        """Callback method from `self._gather_info`. It gets the meaning of the text.

        Args:
            page: A page content from the website.

        Returns:
            Meaning of the text.
        """
        meaning = page.find('div', {'class': 'def ddef_d db'})
        if meaning:
            return meaning.text
        return ''

    def _get_example(self, page: Tag) -> list:
        """Callback method from `self._gather_info`. It gets examples of the text.

        Args:
            page: A page content from the website.

        Returns:
            A list of examples of the text.
        """
        res = []
        examples = page.find_all('span', {'class': 'eg deg'})
        if examples:
            for example in examples:
                res.append(example.text)
        else:
            res.append('')
        return res
