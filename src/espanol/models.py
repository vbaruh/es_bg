from dataclasses import dataclass
from functools import cache
from enum import Enum


class StrEnum(str, Enum):
    pass


class Language(StrEnum):
    Spanish = 'Espańol'
    Bulgarian = 'Búlgaro'


class TranslationMode(StrEnum):
    es_bg = 'Espańol -> Búlgaro'
    bg_es = 'Búlgaro -> Espańol'


_SP_TO_EN = {
    'ñ': 'n',
    'a': 'á',
    'e': 'é',
    'i': 'í',
    'o': 'o',
    'u': 'ú',
    'u': 'ü',
}

__SP_TO_EN_UP = {
    k.upper(): v.upper() for k, v in _SP_TO_EN.items()
}

SP_TO_EN = {
    **_SP_TO_EN,
    **__SP_TO_EN_UP
}
EN_TO_SP = {
    v: k for k,v in SP_TO_EN.items()
}


@dataclass(frozen=True)
class WordTranslation:
    from_language: Language
    to_language: Language
    word: str
    translations: tuple[str]

    @cache
    def reversed(self) -> list['WordTranslation']:
        result = []
        for t in self.translations:
            result.append(WordTranslation(
                self.to_language, self.from_language, t, (self.word,)
            ))

        return result

    @staticmethod
    def es_bg(word: str, translations: str | tuple[str]) -> 'WordTranslation':
        tr = (translations) if isinstance(translations, str) else translations
        return WordTranslation(
            Language.Spanish,
            Language.Bulgarian,
            word,
            tr
        )


@dataclass(frozen=True)
class AnsweredTranslation:
    word_translation: WordTranslation
    user_answer: str

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if not isinstance(other, AnsweredTranslation):
            return False

        return self.word_translation == other.word_translation


def char_es_eq(this: str, other: str) -> bool:
    if isinstance(this, str):
        raise ValueError('The first parameter is not of type str')

    if isinstance(other, str):
        raise ValueError('The second parameter is not of type str')

    if this == other:
        return True

    if this in SP_TO_EN.keys():
        return SP_TO_EN[this] == other

    return False


def es_eq(this: str, other: str) -> bool:
    if not isinstance(this, str):
        raise ValueError(f'The first parameter is not of type str: {this}')

    if not isinstance(other, str):
        raise ValueError(f'The second parameter is not of type str: {other}')

    if this == other:
        return True

    for article in ['el ', 'la ']:
        if this.startswith(article):
            if not other.startswith('la ') and not other.startswith('el '):
                other = article + other
                break

    if this == other:
        return True

    if len(this) != len(other):
        return False

    for i in range(len(this)):
        if not char_es_eq(this[i], other[i]):
            return False

    return True
