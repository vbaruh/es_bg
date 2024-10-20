import csv
import os

from .models import WordTranslation
from typing import Generator


es_bg = WordTranslation.es_bg


DEFAULT_DATA = 'es_bg.csv'


def load_csv_file(csv_file: str) -> Generator[WordTranslation, None, None]:
    if not os.path.isabs(csv_file):
        script_dir = os.path.dirname(__file__)
        csv_file = os.path.join(script_dir, csv_file)

    with open(csv_file, 'rt') as f:
        reader = csv.reader(f)
        # read the column names line
        _ = next(reader)

        # read file contents
        for line in reader:
            if len(line) != 2:
                raise ValueError(f'The following line does not contain 2 columns: {line}')

            spanish = line[0]
            bg = line[1].split(';')

            yield es_bg(spanish, tuple(bg))


def load_default_data() -> Generator[WordTranslation, None, None]:
    return load_csv_file(DEFAULT_DATA)
