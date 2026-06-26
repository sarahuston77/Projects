from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

import ui_theme as theme


def _bind_rounded_rect(widget, rect_attr, radius=None):
    radius = radius or theme.CARD_RADIUS

    def _update(*_args):
        rect = getattr(widget, rect_attr)
        rect.pos = widget.pos
        rect.size = widget.size
        rect.radius = [dp(radius)]

    widget.bind(pos=_update, size=_update)
    _update()
    return _update


class Card(BoxLayout):
    """White card with rounded corners."""

    def __init__(self, bg_color=None, padding=24, spacing=16, **kwargs):
        bg_color = bg_color or theme.SURFACE
        super().__init__(orientation="vertical", padding=dp(padding), spacing=dp(spacing), **kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self._bg = RoundedRectangle(radius=[dp(theme.CARD_RADIUS)])
        _bind_rounded_rect(self, "_bg")


class SectionHeader(BoxLayout):
    def __init__(self, title, subtitle="", **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(72), spacing=dp(4), **kwargs)
        self.title_label = Label(
            text=title,
            font_size=dp(22),
            bold=True,
            color=theme.TEXT_PRIMARY,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(30),
        )
        self.subtitle_label = Label(
            text=subtitle,
            font_size=dp(14),
            color=theme.TEXT_SECONDARY,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
        )
        self.title_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        self.subtitle_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        self.add_widget(self.title_label)
        if subtitle:
            self.add_widget(self.subtitle_label)


class StatusBadge(BoxLayout):
    def __init__(self, text="Waiting", status="waiting", **kwargs):
        super().__init__(size_hint=(None, None), height=dp(30), padding=(dp(12), dp(4)), **kwargs)
        self.status = status
        self.text_label = Label(
            text=text,
            font_size=dp(13),
            bold=True,
            halign="center",
            valign="middle",
        )
        self.add_widget(self.text_label)
        with self.canvas.before:
            self._bg_color = Color()
            self._bg = RoundedRectangle(radius=[dp(14)])
        self.bind(pos=self._sync_bg, size=self._sync_bg)
        self.bind(minimum_width=self._sync_bg)
        self.text_label.bind(
            texture_size=lambda inst, val: setattr(self, "width", val[0] + dp(24))
        )
        self.set_status(status, text)

    def _sync_bg(self, *_args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def set_status(self, status, text=None):
        self.status = status
        if text is not None:
            self.text_label.text = text
        palette = {
            "waiting": theme.PRIMARY_LIGHT,
            "active": (0.98, 0.88, 0.78, 1),
            "success": (0.86, 0.96, 0.90, 1),
        }
        text_colors = {
            "waiting": theme.PRIMARY_DARK,
            "active": theme.ACCENT_ALERT,
            "success": theme.STATUS_SUCCESS,
        }
        self._bg_color.rgba = palette.get(status, theme.PRIMARY_LIGHT)
        self.text_label.color = text_colors.get(status, theme.TEXT_PRIMARY)


class AccentButton(Button):
    def __init__(self, accent_color=None, **kwargs):
        accent_color = accent_color or theme.PRIMARY
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", accent_color)
        kwargs.setdefault("color", theme.TEXT_ON_PRIMARY)
        kwargs.setdefault("font_size", dp(18))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(54))
        super().__init__(**kwargs)


class Spacer(Widget):
    def __init__(self, height=8, **kwargs):
        super().__init__(size_hint_y=None, height=dp(height), **kwargs)
