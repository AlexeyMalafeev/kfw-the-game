class StyleUser:
    style = None  # Style object

    def get_style_string(self, show_emph=False):
        if show_emph:
            emph_info = f'\n {self.style.descr_short}'
        else:
            emph_info = ''
        return f'{self.style.name}{emph_info}'

    def set_style(self, style_name):
        if style_name is not None:
            style_obj = styles.get_style_obj(style_name)
        else:
            style_obj = styles.FLOWER_KUNGFU
        self.style = style_obj
