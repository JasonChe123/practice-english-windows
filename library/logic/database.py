"""
`library/logic/database.py`
\nThis module consists of:
    - `update_database`
    - `get_data`
    - `get_sound`

It reads/ writes data from database.
"""
import requests.models
from kivy.app import App
import pandas as pd
import os
import shutil
import urllib.request


def update_database(word: str, definition: str, example: str, photo: str, sound: requests.models.Response | None) -> bool:
    """
    Write data to the csv file, add image file and mp3 file to the database. Return True if successful, return False if
    the word is empty, or no definition/ example/ photo is found return False.

    Args:
        word: The vocabulary.
        definition: The definition of the vocabulary.
        example: The example of the vocabulary.
        photo: The source link of the photo of the vocabulary.
        sound: The requests' response including bytes code of the mp3 file.
        update_or_add: Use this argument to define

    Return:
        True if update success, False if not success.
    """
    if not any([word, definition, example, photo]):
        return False

    # write csv file
    working_dir = App.get_running_app().working_dir
    db_dir = os.path.join(working_dir, 'database')

    # check file existence
    if 'vocabulary.csv' in os.listdir(db_dir):
        file = os.path.join(db_dir, 'vocabulary.csv')
        df = pd.read_csv(file, encoding='ISO-8859-1')

        # check if the word exists
        all_vocabs = df['Vocabulary'].values.tolist()
        if word.strip() in all_vocabs:
            """need to ask if overwrite"""
            df.drop(df[(df['Vocabulary'] == word)].index, axis=0, inplace=True)

        # gather data
        if '(' in word:
            word = word[:word.find('(')]
        data = {'Vocabulary': [word.strip()],
                'Description': [definition.strip()],
                'Example': [example.strip()]}

        # write database
        df_new = pd.concat([df, pd.DataFrame(data)], ignore_index=True, axis=0)
        try:
            df_new.to_csv(file, index=False)
        except Exception as e:
            print(f"\ndatabase.py->update_database\n{e}")
            return False

        # add image file
        word = word.strip().replace(' ', '_').replace('/', '_').lower()
        if photo.startswith('http'):
            if os.path.basename(photo) != 'no_image.png':
                jpeg = os.path.join(working_dir, 'database', 'images', f'{word}.jpg')
                urllib.request.urlretrieve(photo, jpeg)

        # add sounds file
        if sound:
            src_file = os.path.join(working_dir, 'library', 'sounds', 'temp.mp3')
            dst_file = os.path.join(working_dir, 'database', 'sounds', f"{word}.mp3")
            shutil.copy(src_file, dst_file)

        return True


def get_data(num: int, method: str = 'all') -> pd.DataFrame | None:
    """
    Get vocabulary to practice, it shuffles the whole data first or get the latest data and then shuffle it, depends on
    the method given (latest/ all). Return the data.

    Args:
        num: Number of vocabulary to be extracted.
        method: all/ latest defines the data selection method.

    Returns:
        Dataframe contains the required data to practice/ None if no .csv file in the database.
    """
    # request database
    data = os.path.join(App.get_running_app().working_dir, 'database', 'vocabulary.csv')
    if not os.path.isfile(data):
        return None

    data = pd.read_csv(data).fillna('')
    if method == 'latest':
        # get data -> shuffle
        data = data.iloc[-num:]  # get data
        data = data.sample(frac=1).reset_index(drop=True)  # shuffle
    else:
        # shuffle -> get data
        data = data.sample(frac=1).reset_index(drop=True)  # shuffle
        data = data.iloc[-num:]  # get data

    return data


def get_sound(word: str) -> str | None:
    """
    Get sound file from database.

    Args:
        word: Use this vocabulary as a file name to find the mp3 file from the database.

    Returns:
        File path of the mp3 file. Return None if there is no such mp3 file in the database.
    """
    file = os.path.join(App.get_running_app().working_dir, 'database', 'sounds', f'{word}.mp3')
    if os.path.isfile(file):
        return file

    return None
