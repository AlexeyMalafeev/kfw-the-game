from abc import ABC
from typing import Union

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.kung_fu import styles


class StyleMethods(FighterAPI, ABC):
    def get_style_string(self, show_emph: bool = False) -> str:
        if show_emph:
            emph_info = f'\n {self.style.descr_short}'
        else:
            emph_info = ''
        return f'{self.style.name}{emph_info}'

    def set_style(self, style: Union[styles.Style, str]) -> None:
        if style is not None:
            if isinstance(style, str):
                style_obj = styles.get_style_obj(style)
            elif isinstance(style, styles.Style):
                style_obj = style
            else:
                raise ValueError(f'Incorrect value for style: {style}')
        else:
            style_obj = styles.FLOWER_KUNGFU
        self.style = style_obj
