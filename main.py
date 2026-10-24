import os
import glob
import random
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle, Line, Ellipse, Triangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.widget import Widget

# Optional filechooser for picking custom alarm MP3s
try:
    from plyer import filechooser
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

# Fits comfortably on laptop screen while keeping phone aspect ratio
from kivy.utils import platform
if platform not in ('android', 'ios'):
    Window.size = (360, 680)

# Create 'sounds' folder automatically if it doesn't exist
SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)

# Classic Deadpool Palette
DP_RED = (0.75, 0.06, 0.06, 1)
DP_DARK_RED = (0.45, 0.03, 0.03, 1)
DP_BLACK = (0.06, 0.06, 0.06, 1)
DP_GREY = (0.15, 0.15, 0.15, 1)
DP_WHITE = (1, 1, 1, 1)
DP_YELLOW = (1, 0.85, 0.1, 1)

QUOTES = [
    "\"Time for chimichangas.\"",
    "\"Maximum Effort!\"",
    "\"Wait... am I stuck inside a Poco M7 Plus?!\"",
    "\"Tick-tock. Even my healing factor can't bring back wasted time.\"",
    "\"Drop some Ryan Reynolds MP3s into the 'sounds' folder so I can talk!\"",
    "\"If you snooze the alarm, I'm eating your chimichangas.\"",
    "\"4th wall check: Yes, you sitting at your laptop in VS Code.\""
]


class AudioController:
    """Manages Deadpool voice lines and custom alarm MP3 playback."""
    def __init__(self):
        self.current_voice = None
        self.alarm_sound = None
        self.custom_alarm_path = os.path.join(SOUNDS_DIR, "custom_alarm.mp3")

    def play_voice(self, filename_prefix):
        """Plays a matching MP3 from the 'sounds' folder (e.g., dp_poke1.mp3)."""
        # Stop previous voice clip so they don't talk over each other
        if self.current_voice:
            self.current_voice.stop()

        # Find any mp3 or wav starting with the prefix (e.g., dp_poke*.mp3)
        matches = glob.glob(os.path.join(SOUNDS_DIR, f"{filename_prefix}*.mp3")) + \
                  glob.glob(os.path.join(SOUNDS_DIR, f"{filename_prefix}*.wav"))

        if matches:
            chosen_clip = random.choice(matches)
            self.current_voice = SoundLoader.load(chosen_clip)
            if self.current_voice:
                self.current_voice.play()
                return os.path.basename(chosen_clip)
        return None

    def start_alarm_audio(self):
        """Plays the custom alarm MP3 on loop."""
        self.stop_alarm_audio()
        if os.path.exists(self.custom_alarm_path):
            self.alarm_sound = SoundLoader.load(self.custom_alarm_path)
            if self.alarm_sound:
                self.alarm_sound.loop = True
                self.alarm_sound.play()
                return True
        return False

    def stop_alarm_audio(self):
        if self.alarm_sound:
            self.alarm_sound.stop()
            self.alarm_sound = None


AUDIO = AudioController()


class DeadpoolLogo(Widget):
    """Draws the custom Deadpool mask emblem."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw_mask, size=self.draw_mask)

    def draw_mask(self, *args):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.42

        with self.canvas:
            Color(*DP_RED)
            Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
            Color(*DP_BLACK)
            Line(circle=(cx, cy, r), width=2)
            Line(points=[cx, cy - r, cx, cy + r], width=1.5)

            patch_w, patch_h = r * 0.65, r * 0.95
            Ellipse(pos=(cx - r * 0.78, cy - patch_h * 0.48), size=(patch_w, patch_h))
            Ellipse(pos=(cx + r * 0.13, cy - patch_h * 0.48), size=(patch_w, patch_h))

            Color(*DP_WHITE)
            Triangle(points=[
                cx - r * 0.62, cy + r * 0.08,
                cx - r * 0.22, cy - r * 0.08,
                cx - r * 0.55, cy - r * 0.12
            ])
            Triangle(points=[
                cx + r * 0.62, cy + r * 0.12,
                cx + r * 0.22, cy - r * 0.05,
                cx + r * 0.55, cy - r * 0.10
            ])


# ----------------- TAB 1: LIVE CLOCK -----------------
class ClockScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        self.logo = DeadpoolLogo(size_hint=(1, 0.26))
        layout.add_widget(self.logo)

        self.time_label = Label(
            text="00:00:00",
            font_size='44sp',
            bold=True,
            color=DP_WHITE,
            size_hint=(1, 0.22)
        )
        layout.add_widget(self.time_label)

        self.date_label = Label(
            text="LOADING...",
            font_size='15sp',
            bold=True,
            color=DP_YELLOW,
            size_hint=(1, 0.08)
        )
        layout.add_widget(self.date_label)

        self.quote_label = Label(
            text=random.choice(QUOTES),
            font_size='14sp',
            italic=True,
            halign="center",
            valign="middle",
            color=DP_RED,
            size_hint=(1, 0.22)
        )
        self.quote_label.bind(size=self.quote_label.setter('text_size'))
        layout.add_widget(self.quote_label)

        self.quips_btn = Button(
            text="POKE DEADPOOL (VOICE)",
            font_size='15sp',
            bold=True,
            background_normal='',
            background_color=DP_RED,
            color=DP_WHITE,
            size_hint=(1, 0.14)
        )
        self.quips_btn.bind(on_press=self.change_quote)
        layout.add_widget(self.quips_btn)

        self.add_widget(layout)

    def change_quote(self, instance):
        self.quote_label.text = random.choice(QUOTES)
        played = AUDIO.play_voice("dp_poke")
        if not played:
            self.quote_label.text += "\n[Put dp_poke1.mp3 in /sounds folder for Ryan's voice!]"


# ----------------- TAB 2: ALARM -----------------
class AlarmScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alarm_hour = 7
        self.alarm_min = 0
        self.alarm_ampm = "AM"
        self.alarm_active = False
        self.alarm_ringing = False

        layout = BoxLayout(orientation='vertical', padding=12, spacing=8)

        title = Label(
            text="[b]WAKE UP, WOLVERINE[/b]",
            markup=True,
            font_size='18sp',
            color=DP_YELLOW,
            size_hint=(1, 0.10)
        )
        layout.add_widget(title)

        self.alarm_display = Label(
            text="07:00 AM",
            font_size='44sp',
            bold=True,
            color=DP_WHITE,
            size_hint=(1, 0.20)
        )
        layout.add_widget(self.alarm_display)

        # Controls Row (+ / - Hour, Min, AM/PM)
        controls = BoxLayout(orientation='horizontal', spacing=8, size_hint=(1, 0.24))

        hr_box = BoxLayout(orientation='vertical', spacing=5)
        btn_hr_up = Button(text="+ HR", bold=True, background_normal='', background_color=DP_GREY)
        btn_hr_dn = Button(text="- HR", bold=True, background_normal='', background_color=DP_GREY)
        btn_hr_up.bind(on_press=lambda x: self.adjust_time(1, 0))
        btn_hr_dn.bind(on_press=lambda x: self.adjust_time(-1, 0))
        hr_box.add_widget(btn_hr_up)
        hr_box.add_widget(btn_hr_dn)

        min_box = BoxLayout(orientation='vertical', spacing=5)
        btn_min_up = Button(text="+ MIN", bold=True, background_normal='', background_color=DP_GREY)
        btn_min_dn = Button(text="- MIN", bold=True, background_normal='', background_color=DP_GREY)
        btn_min_up.bind(on_press=lambda x: self.adjust_time(0, 1))
        btn_min_dn.bind(on_press=lambda x: self.adjust_time(0, -1))
        min_box.add_widget(btn_min_up)
        min_box.add_widget(btn_min_dn)

        btn_ampm = Button(text="AM / PM", bold=True, background_normal='', background_color=DP_DARK_RED)
        btn_ampm.bind(on_press=self.toggle_ampm)

        controls.add_widget(hr_box)
        controls.add_widget(min_box)
        controls.add_widget(btn_ampm)
        layout.add_widget(controls)

        # Custom Audio Picker Button
        self.pick_sound_btn = Button(
            text="CHOOSE CUSTOM ALARM MP3",
            font_size='13sp',
            bold=True,
            background_normal='',
            background_color=DP_DARK_RED,
            color=DP_YELLOW,
            size_hint=(1, 0.12)
        )
        self.pick_sound_btn.bind(on_press=self.choose_custom_mp3)
        layout.add_widget(self.pick_sound_btn)

        self.status_label = Label(
            text="SOUND: custom_alarm.mp3 | DISARMED",
            font_size='13sp',
            color=(0.75, 0.75, 0.75, 1),
            size_hint=(1, 0.12)
        )
        layout.add_widget(self.status_label)

        self.toggle_btn = Button(
            text="ARM ALARM",
            font_size='16sp',
            bold=True,
            background_normal='',
            background_color=DP_RED,
            size_hint=(1, 0.14)
        )
        self.toggle_btn.bind(on_press=self.toggle_alarm)
        layout.add_widget(self.toggle_btn)

        self.add_widget(layout)

    def choose_custom_mp3(self, instance):
        if HAS_PLYER:
            filechooser.open_file(
                on_selection=self.on_file_picked,
                filters=[("Audio Files", "*.mp3", "*.wav")]
            )
        else:
            self.status_label.text = "Put 'custom_alarm.mp3' in /sounds folder!"

    def on_file_picked(self, selection):
        if selection:
            AUDIO.custom_alarm_path = selection[0]
            filename = os.path.basename(selection[0])
            self.status_label.text = f"CUSTOM SOUND SET: {filename}"
            self.status_label.color = DP_YELLOW

    def update_display(self):
        self.alarm_display.text = f"{self.alarm_hour:02d}:{self.alarm_min:02d} {self.alarm_ampm}"

    def adjust_time(self, d_hr, d_min):
        self.alarm_hour = ((self.alarm_hour - 1 + d_hr) % 12) + 1
        self.alarm_min = (self.alarm_min + d_min) % 60
        self.update_display()

    def toggle_ampm(self, instance):
        self.alarm_ampm = "PM" if self.alarm_ampm == "AM" else "AM"
        self.update_display()

    def toggle_alarm(self, instance):
        if self.alarm_ringing:
            self.alarm_ringing = False
            self.alarm_active = False
            AUDIO.stop_alarm_audio()
            self.toggle_btn.text = "ARM ALARM"
            self.toggle_btn.background_color = DP_RED
            self.toggle_btn.color = DP_WHITE
            self.status_label.text = "Good morning, sunshine. Alarm stopped."
            self.status_label.color = (0.7, 0.7, 0.7, 1)
            return

        self.alarm_active = not self.alarm_active
        if self.alarm_active:
            self.toggle_btn.text = "DISARM ALARM"
            self.toggle_btn.background_color = DP_GREY
            self.status_label.text = f"ARMED FOR {self.alarm_display.text}!"
            self.status_label.color = DP_YELLOW
        else:
            self.toggle_btn.text = "ARM ALARM"
            self.toggle_btn.background_color = DP_RED
            self.status_label.text = "ALARM STATUS: DISARMED"
            self.status_label.color = (0.7, 0.7, 0.7, 1)


# ----------------- TAB 3: STOPWATCH -----------------
class StopwatchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sw_seconds = 0.0
        self.sw_running = False

        layout = BoxLayout(orientation='vertical', padding=15, spacing=12)

        title = Label(
            text="[b]MAXIMUM EFFORT TIMER[/b]",
            markup=True,
            font_size='18sp',
            color=DP_YELLOW,
            size_hint=(1, 0.15)
        )
        layout.add_widget(title)

        self.sw_label = Label(
            text="00:00.00",
            font_size='50sp',
            bold=True,
            color=DP_WHITE,
            size_hint=(1, 0.35)
        )
        layout.add_widget(self.sw_label)

        self.voice_status = Label(
            text="Deadpool Voice: Ready",
            font_size='13sp',
            italic=True,
            color=DP_RED,
            size_hint=(1, 0.12)
        )
        layout.add_widget(self.voice_status)

        btn_row = BoxLayout(orientation='horizontal', spacing=12, size_hint=(1, 0.18))
        self.start_btn = Button(
            text="START",
            font_size='16sp',
            bold=True,
            background_normal='',
            background_color=DP_RED
        )
        self.reset_btn = Button(
            text="RESET",
            font_size='16sp',
            bold=True,
            background_normal='',
            background_color=DP_GREY
        )
        self.start_btn.bind(on_press=self.start_stop)
        self.reset_btn.bind(on_press=self.reset_sw)

        btn_row.add_widget(self.start_btn)
        btn_row.add_widget(self.reset_btn)
        layout.add_widget(btn_row)

        self.add_widget(layout)
        Clock.schedule_interval(self.update_sw, 0.05)

    def start_stop(self, instance):
        self.sw_running = not self.sw_running
        if self.sw_running:
            self.start_btn.text = "PAUSE"
            self.start_btn.background_color = DP_DARK_RED
            clip = AUDIO.play_voice("dp_timer_start")
            self.voice_status.text = f"Playing: {clip}" if clip else "\"Maximum Effort! Go, go, go!\""
        else:
            self.start_btn.text = "RESUME"
            self.start_btn.background_color = DP_RED
            clip = AUDIO.play_voice("dp_timer_stop")
            self.voice_status.text = f"Playing: {clip}" if clip else "\"Time froze! Taking a breather?\""

    def reset_sw(self, instance):
        self.sw_running = False
        self.sw_seconds = 0.0
        self.sw_label.text = "00:00.00"
        self.start_btn.text = "START"
        self.start_btn.background_color = DP_RED
        AUDIO.play_voice("dp_timer_stop")
        self.voice_status.text = "\"Wiped clean. Like my browser history.\""

    def update_sw(self, dt):
        if self.sw_running:
            self.sw_seconds += dt
            mins, secs = divmod(self.sw_seconds, 60)
            hundredths = int((secs - int(secs)) * 100)
            self.sw_label.text = f"{int(mins):02d}:{int(secs):02d}.{hundredths:02d}"


# ----------------- MAIN SHELL & NAVIGATION -----------------
class DeadpoolRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=12, spacing=8, **kwargs)

        with self.canvas.before:
            Color(*DP_BLACK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(*DP_RED)
            self.border_line = Line(rectangle=(self.x + 6, self.y + 6, self.width - 12, self.height - 12), width=2.2)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

        header = Label(
            text="[b]DEADPOOL // POCO M7 EDITION[/b]",
            markup=True,
            font_size='16sp',
            color=DP_RED,
            size_hint=(1, 0.08)
        )
        self.add_widget(header)

        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        self.clock_screen = ClockScreen(name='clock')
        self.alarm_screen = AlarmScreen(name='alarm')
        self.sw_screen = StopwatchScreen(name='stopwatch')

        self.sm.add_widget(self.clock_screen)
        self.sm.add_widget(self.alarm_screen)
        self.sm.add_widget(self.sw_screen)
        self.add_widget(self.sm)

        nav_bar = BoxLayout(orientation='horizontal', spacing=6, size_hint=(1, 0.11))
        self.btn_nav_clock = Button(text="CLOCK", bold=True, background_normal='', background_color=DP_RED)
        self.btn_nav_alarm = Button(text="ALARM", bold=True, background_normal='', background_color=DP_GREY)
        self.btn_nav_sw = Button(text="TIMER", bold=True, background_normal='', background_color=DP_GREY)

        self.btn_nav_clock.bind(on_press=lambda x: self.switch_tab('clock'))
        self.btn_nav_alarm.bind(on_press=lambda x: self.switch_tab('alarm'))
        self.btn_nav_sw.bind(on_press=lambda x: self.switch_tab('stopwatch'))

        nav_bar.add_widget(self.btn_nav_clock)
        nav_bar.add_widget(self.btn_nav_alarm)
        nav_bar.add_widget(self.btn_nav_sw)
        self.add_widget(nav_bar)

        Clock.schedule_interval(self.master_tick, 1)
        self.master_tick(0)

    def switch_tab(self, tab_name):
        self.sm.current = tab_name
        self.btn_nav_clock.background_color = DP_RED if tab_name == 'clock' else DP_GREY
        self.btn_nav_alarm.background_color = DP_RED if tab_name == 'alarm' else DP_GREY
        self.btn_nav_sw.background_color = DP_RED if tab_name == 'stopwatch' else DP_GREY

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rectangle = (self.x + 6, self.y + 6, self.width - 12, self.height - 12)

    def master_tick(self, dt):
        now = datetime.now()
        current_time_str = now.strftime("%I:%M:%S %p")
        current_hm = now.strftime("%I:%M %p")

        self.clock_screen.time_label.text = current_time_str
        self.clock_screen.date_label.text = now.strftime("%A, %d %B %Y").upper()

        # Check Alarm Trigger
        if self.alarm_screen.alarm_active and not self.alarm_screen.alarm_ringing:
            if current_hm == self.alarm_screen.alarm_display.text and now.second == 0:
                self.trigger_alarm()

        # Fallback system beep if no custom MP3 is found
        if self.alarm_screen.alarm_ringing and not AUDIO.alarm_sound:
            print("\a", end="", flush=True)

    def trigger_alarm(self):
        self.alarm_screen.alarm_ringing = True
        self.switch_tab('alarm')
        played_custom = AUDIO.start_alarm_audio()
        if played_custom:
            self.alarm_screen.status_label.text = "WAKE UP!! PLAYING CUSTOM ALARM!!"
        else:
            self.alarm_screen.status_label.text = "WAKE UP!! (Add custom_alarm.mp3 for music!)"
        self.alarm_screen.status_label.color = DP_RED
        self.alarm_screen.toggle_btn.text = "STOP ALARM!!"
        self.alarm_screen.toggle_btn.background_color = DP_YELLOW
        self.alarm_screen.toggle_btn.color = DP_BLACK


class DeadpoolClockApp(App):
    def build(self):
        self.title = "Deadpool Clock v3.0 (Audio Edition)"
        return DeadpoolRoot()


if __name__ == '__main__':
    DeadpoolClockApp().run()