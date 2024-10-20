'''Welcome to Reflex! This file outlines the steps to create a basic app.'''

import reflex as rx
import secrets

from rxconfig import config
from dataclasses import dataclass, field
from typing import Optional
from functools import cache
from .models import WordTranslation, AnsweredTranslation, TranslationMode, Language
from .translation_data import load_default_data

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@cache
def get_default_es_bg_translations(tm: TranslationMode):
    raw: list[WordTranslation] = list(load_default_data())
    if tm == TranslationMode.es_bg:
        return raw
    else:
        return [
            r
            for w in raw
            for r in w.reversed()
        ]


@dataclass
class TranslationModeState:
    word: Optional[WordTranslation] = None
    is_answered: bool = False
    answered_list: list[AnsweredTranslation] = field(default_factory=list)


class State(rx.State):
    es_bg: TranslationModeState = TranslationModeState()
    bg_es: TranslationModeState = TranslationModeState()

    trans_mode: TranslationMode = TranslationMode.es_bg

    def on_trans_mode_change(self, value):
        self.trans_mode = value

    def on_submit(self, form_data: dict) -> None:
        current: TranslationModeState = self._get_current()
        logger.info('form_data: %s', form_data)
        logger.info('current: %s', current)

        if self._is_ready_for_next_word():
            logger.info('It is ready for next word, will get a new one.')
            current.word = self._get_next_word()

            current.is_answered = False
            logger.info('Found %s', current.word)
            return

        if 'user_translation' not in form_data:
            return

        user_translation = form_data['user_translation']
        if not user_translation:
            return

        current.answered_list.insert(0, AnsweredTranslation(
            current.word,
            user_translation
        ))
        current.is_answered = True

    @rx.var
    def get_current_word(self) -> str:
        current: TranslationModeState = self._get_current()
        logger.info('get_current_word current: %s', current)

        if current.word:
            return current.word.word
        else:
            return '-'

    @rx.var
    def is_ready_for_next_word(self) -> bool:
        return self._is_ready_for_next_word()

    @rx.var
    def is_answered(self) -> bool:
        current: TranslationModeState = self._get_current()

        return current.is_answered

    @rx.var
    def answered_list(self) -> list[AnsweredTranslation]:
        current: TranslationModeState = self._get_current()

        return rx.Var.create(current.answered_list)

    @rx.var
    def word(self) -> WordTranslation:
        current: TranslationModeState = self._get_current()

        return current.word

    def _is_ready_for_next_word(self) -> bool:
        current: TranslationModeState = self._get_current()
        logger.info('_is_ready_for_next_word current: %s', current)

        return (not current.word) or (current.is_answered)

    def _get_next_word(self) -> Optional[WordTranslation]:
        if self._is_all_answered():
            return None

        while True:
            next = secrets.choice(get_default_es_bg_translations(self.trans_mode))
            if not self._is_answered(next):
                return next

    def _is_answered(self, word: WordTranslation) -> bool:
        current: TranslationModeState = self._get_current()

        return AnsweredTranslation(word, '') in current.answered_list

    def _is_all_answered(self) -> bool:
        current: TranslationModeState = self._get_current()

        return len(current.answered_list) == len(get_default_es_bg_translations(self.trans_mode))

    def _get_current(self) -> TranslationModeState:
        if self.trans_mode == TranslationMode.es_bg:
            return self.es_bg
        else:
            return self.bg_es


def index() -> rx.Component:

    def _render_answer_table_row(at: AnsweredTranslation) -> rx.Component:

        def _translation(t: str):
            return rx.hstack(
                rx.icon('dot'),
                rx.text(t)
            )

        return rx.table.row(
            rx.table.cell(at.word_translation.word),
            rx.table.cell(
                rx.vstack(rx.foreach(at.word_translation.translations, _translation))
            ),
            rx.table.cell(
                rx.hstack(
                    rx.cond(
                        at.word_translation.translations.contains(at.user_answer),
                        rx.icon('circle-check', color='green'),
                        rx.icon('circle-x', color='red')
                    ),
                    rx.text(
                        at.user_answer,
                        color_scheme=rx.cond(
                            at.word_translation.translations.contains(at.user_answer),
                            'green',
                            'red'
                        )
                    )
                )
            )
        )

    return rx.container(
        rx.color_mode.button(position='top-right'),
        rx.vstack(
            rx.heading('¡Practica la lengua española!', size='9'),
            rx.hstack(
                rx.text('Modo'),
                rx.select(
                    [TranslationMode.es_bg, TranslationMode.bg_es],
                    value=State.trans_mode,
                    on_change=[
                        State.on_trans_mode_change,
                        rx.set_value('user_translation', '')
                    ]
                )
            ),
            rx.hstack(
                rx.text('Palabra para traducir: '),
                rx.text(State.get_current_word, weight='bold'),
                rx.cond(
                    State.is_answered,
                        rx.cond(
                            State.answered_list[0].word_translation.translations.contains(State.answered_list[0].user_answer),
                            rx.icon('circle-check', color='green'),
                            rx.icon('circle-x', color='red')
                        )
                )
            ),
            rx.form.root(
                rx.input(
                    id='user_translation',
                    name='user_translation',
                    placeholder='Introduce tu traducción',
                    type='text',
                ),

                rx.cond(
                    State.is_ready_for_next_word,
                    rx.button('Siguiente palabra', type='submit', on_click=[rx.set_value('user_translation', '')], auto_focus=True),
                    rx.button('Comprobar traducción', type='submit'),
                ),

                on_submit=State.on_submit
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell('Palabra'),
                        rx.table.column_header_cell('Traducción'),
                        rx.table.column_header_cell('Traducción del usuario'),
                    ),
                ),
                rx.table.body(
                    rx.foreach(State.answered_list, _render_answer_table_row)
                ),
                width='100%',
            )
        ),
    )


app = rx.App()
app.add_page(index)
