from ._base_fighter import BaseFighter
from ...kung_fu import styles


class StyleMethods(BaseFighter):
    def get_style_string(self, show_emph=False):
        if show_emph:
            emph_info = f'\n {self.style.descr_short}'
        else:
            emph_info = ''
        return f'{self.style.name}{emph_info}'

    def set_style(self, style):
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
