from abc import ABC
from typing import Union

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.kung_fu import styles


class StyleMethods(FighterAPI, ABC):
    def get_displayed_style_name(self) -> str:
        """The style's true name is only shown to a human player who has learned the
        secret technique of their own style; everyone else sees the public name."""
        if self.is_human and self.knows_style_secret():
            return self.style.name
        return self.style.public_name

    def get_displayed_style_emph(self) -> str:
        if self.is_human and self.knows_style_secret():
            return self.style.descr_short
        return self.style.public_descr_short

    def get_style_string(self, show_emph: bool = False) -> str:
        if show_emph:
            emph_info = f'\n {self.get_displayed_style_emph()}'
        else:
            emph_info = ''
        return f'{self.get_displayed_style_name()}{emph_info}'

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
