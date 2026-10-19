import math, random, time
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.window import Window

BLUE = (0.1, 0.7, 1, 1)
Window.clearcolor = (0.01, 0.03, 0.08, 1)


class Core(FloatLayout):
    """Live rotating rings + pulsing glow around the Jarvis face."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.t = 0
        self.active = False
        self.add_widget(Image(source="jarvis_icon.png", size_hint=(0.62, 0.62),
                              pos_hint={"center_x": .5, "center_y": .5}))
        Clock.schedule_interval(self.draw, 1 / 30)

    def draw(self, dt):
        self.t += dt * (2.2 if self.active else 1)
        self.canvas.before.clear()
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) / 2
        pulse = 0.5 + 0.5 * math.sin(self.t * (4 if self.active else 2))
        with self.canvas.before:
            Color(0.1, 0.6, 1, 0.10 + 0.15 * pulse)
            g = r * (0.95 + 0.05 * pulse)
            Ellipse(pos=(cx - g, cy - g), size=(2 * g, 2 * g))
            for i, (rad, speed, width) in enumerate([(0.95, 40, 3), (0.82, -65, 2), (0.70, 90, 1.5)]):
                Color(0.1, 0.75, 1, 0.9 - i * 0.2)
                a = (self.t * speed) % 360
                for k in range(3):
                    s = a + k * 120
                    Line(circle=(cx, cy, r * rad, s, s + 70), width=width)


class Wave(Widget):
    """Live audio-style waveform; moves only while listening."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.active = False
        Clock.schedule_interval(self.draw, 1 / 20)

    def draw(self, dt):
        self.canvas.clear()
        n, t = 28, time.time()
        bw = self.width / n
        with self.canvas:
            Color(*BLUE)
            for i in range(n):
                if self.active:
                    h = (0.25 + 0.75 * abs(math.sin(t * 6 + i * 0.7)) * random.uniform(0.5, 1)) * self.height
                else:
                    h = 0.06 * self.height
                Rectangle(pos=(self.x + i * bw + 2, self.center_y - h / 2), size=(bw - 4, h))


class JarvisApp(App):
    title = "Jarvis"

    def build(self):
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)
        root.add_widget(Label(text="JARVIS  AI  ASSISTANT", font_size="22sp", bold=True,
                              color=BLUE, size_hint_y=None, height=48))
        self.clock = Label(text="", color=(0.5, 0.8, 1, 1), size_hint_y=None, height=24)
        root.add_widget(self.clock)
        self.core = Core(size_hint_y=0.5)
        root.add_widget(self.core)
        self.wave = Wave(size_hint_y=None, height=60)
        root.add_widget(self.wave)
        self.status = Label(text="TAP TO SPEAK", color=BLUE, size_hint_y=None, height=32)
        root.add_widget(self.status)
        sv = ScrollView(size_hint_y=0.25)
        self.log = Label(text="Jarvis: Hello! How can I help you today?", size_hint_y=None,
                         halign="left", valign="top", color=(0.8, 0.95, 1, 1))
        self.log.bind(width=lambda *a: setattr(self.log, "text_size", (self.log.width, None)),
                      texture_size=lambda *a: setattr(self.log, "height", self.log.texture_size[1]))
        sv.add_widget(self.log)
        root.add_widget(sv)
        self.btn = Button(text="MIC", size_hint_y=None, height=64, font_size="20sp",
                          background_color=(0.05, 0.4, 0.8, 1), on_release=self.toggle)
        root.add_widget(self.btn)
        Clock.schedule_interval(lambda dt: setattr(self.clock, "text", time.strftime("%I:%M:%S %p")), 1)
        self.ask_permissions()
        return root

    def ask_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.RECORD_AUDIO, Permission.READ_CONTACTS,
                                 Permission.CALL_PHONE])
        except Exception:
            pass  # not on Android

    def toggle(self, *a):
        on = not self.core.active
        self.core.active = self.wave.active = on
        self.status.text = "LISTENING..." if on else "TAP TO SPEAK"
        self.btn.text = "STOP" if on else "MIC"


if __name__ == "__main__":
    JarvisApp().run()
