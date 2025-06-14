# belot_app.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation
from random import shuffle

# Window setup
Window.size = (720, 1280)
Window.clearcolor = (1, 1, 1, 1)

PRIMARY_COLOR = (0, 0, 0, 1)
ACCENT_COLOR = (1, 0.2, 0.4, 1)
BUTTON_BG = (0.9, 0.9, 0.9, 1)

translations = {
    'en': {
        'title': "Belot Score Counter",
        'start_game': "Start Game",
        'pick_teams': "Pick Teams",
        'enter_team_a': "Team A",
        'enter_team_b': "Team B",
        'round': "Round",
        'submit_scores': "Submit",
        'undo': "Undo",
        'restart': "Restart",
        'score_error': "Invalid input.",
        'negative_error': "No negative scores.",
        'undo_error': "Nothing to undo.",
        'undo_success': "Undone.",
        'team_a_wins': "{} wins!",
        'team_b_wins': "{} wins!",
        'tie': "Tie!",
        'game_over': "Game Over",
        'score_text': "{}: {} | {}: {}",
        'lang_toggle': "BG",
        'back': "Back"
    },
    'bg': {
        'title': "Калкулатор за белот",
        'start_game': "Старт",
        'pick_teams': "Избор на отбори",
        'enter_team_a': "Отбор A",
        'enter_team_b': "Отбор B",
        'round': "Рунд",
        'submit_scores': "Изпрати",
        'undo': "Назад",
        'restart': "Рестарт",
        'score_error': "Невалидни данни.",
        'negative_error': "Без отрицателни точки.",
        'undo_error': "Няма какво да се отмени.",
        'undo_success': "Отменено.",
        'team_a_wins': "{} печели!",
        'team_b_wins': "{} печели!",
        'tie': "Равенство!",
        'game_over': "Край",
        'score_text': "{}: {} | {}: {}",
        'lang_toggle': "EN",
        'back': "Назад"
    }
}

current_language = 'en'

class Input(TextInput):
    def __init__(self, **kwargs):
        super().__init__(
            multiline=False,
            font_size='18sp',
            background_color=(1, 1, 1, 1),
            foreground_color=PRIMARY_COLOR,
            cursor_color=ACCENT_COLOR,
            hint_text_color=(0.5, 0.5, 0.5, 1),
            padding=[12, 10],
            size_hint=(1, None),
            height=60,
            **kwargs
        )

class KButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_color', ACCENT_COLOR)
        kwargs.setdefault('color', (1, 1, 1, 1))
        kwargs.setdefault('font_size', '18sp')
        kwargs.setdefault('size_hint', (1, None))
        kwargs.setdefault('height', 60)
        super().__init__(**kwargs)

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        anchor = AnchorLayout()
        layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.9, 0.9))

        self.title_label = Label(font_size='32sp', bold=True, color=PRIMARY_COLOR, size_hint=(1, None), height=80)
        self.team_a_input = Input()
        self.team_b_input = Input()

        self.start_btn = KButton()
        self.start_btn.bind(on_press=self.start_game)

        self.chwazi_btn = KButton()
        self.chwazi_btn.bind(on_press=self.go_to_chwazi)

        self.lang_btn = Button(
            background_normal='',
            background_color=BUTTON_BG,
            color=PRIMARY_COLOR,
            font_size='16sp',
            size_hint=(1, None),
            height=50
        )
        self.lang_btn.bind(on_press=self.toggle_language)

        layout.add_widget(self.title_label)
        layout.add_widget(self.team_a_input)
        layout.add_widget(self.team_b_input)
        layout.add_widget(self.start_btn)
        layout.add_widget(self.chwazi_btn)
        layout.add_widget(self.lang_btn)

        anchor.add_widget(layout)
        self.add_widget(anchor)
        self.refresh_texts()

    def refresh_texts(self):
        t = translations[current_language]
        self.title_label.text = t['title']
        self.team_a_input.hint_text = t['enter_team_a']
        self.team_b_input.hint_text = t['enter_team_b']
        self.start_btn.text = t['start_game']
        self.chwazi_btn.text = t['pick_teams']
        self.lang_btn.text = t['lang_toggle']

    def toggle_language(self, instance):
        App.get_running_app().switch_language()

    def start_game(self, instance):
        a = self.team_a_input.text.strip() or "Team A"
        b = self.team_b_input.text.strip() or "Team B"
        self.manager.get_screen('game').set_team_names(a, b)
        self.manager.transition.direction = 'left'
        self.manager.current = 'game'

    def go_to_chwazi(self, instance):
        self.manager.transition.direction = 'up'
        self.manager.current = 'chwazi'

class BelotGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team_a_name = "Team A"
        self.team_b_name = "Team B"
        self.team_a_score = 0
        self.team_b_score = 0
        self.round_num = 1
        self.history = []

        anchor = AnchorLayout()
        layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(0.9, 0.95))

        self.header = Label(font_size='28sp', bold=True, color=PRIMARY_COLOR, size_hint=(1, None), height=70)
        self.round_label = Label(font_size='20sp', color=PRIMARY_COLOR, size_hint=(1, None), height=40)

        input_grid = GridLayout(cols=2, spacing=10, size_hint=(1, None), height=60)
        self.input_a = Input()
        self.input_b = Input()
        input_grid.add_widget(self.input_a)
        input_grid.add_widget(self.input_b)

        self.submit_btn = KButton()
        self.submit_btn.bind(on_press=self.submit_scores)

        control_box = BoxLayout(spacing=10, size_hint=(1, None), height=60)
        self.undo_btn = KButton(background_color=(0.3, 0.3, 0.3, 1))
        self.restart_btn = KButton(background_color=(1, 0.1, 0.1, 1))
        self.undo_btn.bind(on_press=self.undo_round)
        self.restart_btn.bind(on_press=self.restart_game)
        control_box.add_widget(self.undo_btn)
        control_box.add_widget(self.restart_btn)

        self.score_label = Label(font_size='18sp', color=PRIMARY_COLOR, size_hint=(1, None), height=40)
        self.message_label = Label(font_size='16sp', color=(1, 0, 0, 1), size_hint=(1, None), height=40)

        layout.add_widget(self.header)
        layout.add_widget(self.round_label)
        layout.add_widget(input_grid)
        layout.add_widget(self.submit_btn)
        layout.add_widget(control_box)
        layout.add_widget(self.score_label)
        layout.add_widget(self.message_label)

        anchor.add_widget(layout)
        self.add_widget(anchor)
        self.refresh_texts()

    def refresh_texts(self):
        t = translations[current_language]
        self.header.text = t['title']
        self.submit_btn.text = t['submit_scores']
        self.undo_btn.text = t['undo']
        self.restart_btn.text = t['restart']
        self.input_a.hint_text = self.team_a_name
        self.input_b.hint_text = self.team_b_name
        self.update_labels()

    def set_team_names(self, a, b):
        self.team_a_name = a
        self.team_b_name = b
        self.refresh_texts()

    def update_labels(self):
        t = translations[current_language]
        self.round_label.text = f"{t['round']} {self.round_num}"
        self.score_label.text = t['score_text'].format(self.team_a_name, self.team_a_score, self.team_b_name, self.team_b_score)

    def submit_scores(self, instance):
        t = translations[current_language]
        try:
            a_points = int(self.input_a.text)
            b_points = int(self.input_b.text)
        except ValueError:
            self.message_label.text = t['score_error']
            return
        if a_points < 0 or b_points < 0:
            self.message_label.text = t['negative_error']
            return

        self.history.append((self.team_a_score, self.team_b_score, self.round_num))
        self.team_a_score += a_points
        self.team_b_score += b_points
        self.round_num += 1
        self.input_a.text = ''
        self.input_b.text = ''
        self.message_label.text = ''
        self.update_labels()

        if self.team_a_score >= 151 or self.team_b_score >= 151:
            self.submit_btn.disabled = True
            if self.team_a_score > self.team_b_score:
                self.message_label.text = t['team_a_wins'].format(self.team_a_name)
            elif self.team_b_score > self.team_a_score:
                self.message_label.text = t['team_b_wins'].format(self.team_b_name)
            else:
                self.message_label.text = t['tie']
            self.round_label.text = t['game_over']

    def undo_round(self, instance):
        t = translations[current_language]
        if not self.history:
            self.message_label.text = t['undo_error']
            return
        self.team_a_score, self.team_b_score, self.round_num = self.history.pop()
        self.update_labels()
        self.message_label.text = t['undo_success']
        self.submit_btn.disabled = False

    def restart_game(self, instance):
        self.team_a_score = 0
        self.team_b_score = 0
        self.round_num = 1
        self.history = []
        self.input_a.text = ''
        self.input_b.text = ''
        self.message_label.text = ''
        self.submit_btn.disabled = False
        self.update_labels()

class PlayerCircle(Widget):
    def __init__(self, touch, color, **kwargs):
        super().__init__(**kwargs)
        self.touch = touch
        self.color = color
        self.size = (100, 100)
        self.pos = (touch.x - 50, touch.y - 50)
        with self.canvas:
            self.color_instr = Color(*self.color, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

    def update_color(self, new_color):
        self.color = new_color
        self.color_instr.rgb = new_color

    def fade_out(self, callback=None):
        anim = Animation(a=0, duration=1.0)
        anim.bind(on_progress=self._update_alpha)
        if callback:
            anim.bind(on_complete=lambda *_: callback(self))
        anim.start(self.color_instr)

    def _update_alpha(self, anim, widget, progress):
        self.color_instr.a = 1 - progress

class ChwaziWidget(Widget):
    max_players = 4
    touch_colors = [(1, 0, 0), (0, 1, 0), (0, 0.8, 1), (1, 0.6, 0)]
    team_colors = [(1, 1, 0), (0.6, 0, 1)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_circles = {}
        self.teams_assigned = False

    def on_touch_down(self, touch):
        if self.teams_assigned or touch.uid in self.player_circles:
            return
        if len(self.player_circles) >= self.max_players:
            return

        color = self.touch_colors[len(self.player_circles)]
        circle = PlayerCircle(touch, color)
        self.add_widget(circle)
        self.player_circles[touch.uid] = circle

        if len(self.player_circles) == self.max_players:
            Clock.schedule_once(self.assign_teams, 3)

    def on_touch_up(self, touch):
        if touch.uid in self.player_circles:
            del self.player_circles[touch.uid]

        if self.teams_assigned and not self.player_circles:
            for circle in self.children[:]:
                if isinstance(circle, PlayerCircle):
                    circle.fade_out(callback=self.remove_widget)

    def assign_teams(self, dt):
        if len(self.player_circles) < self.max_players:
            return

        self.teams_assigned = True
        circles = list(self.player_circles.values())
        shuffle(circles)
        team1, team2 = circles[:2], circles[2:]

        for team, color in zip([team1, team2], self.team_colors):
            for circle in team:
                circle.update_color(color)

class ChwaziScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.chwazi = ChwaziWidget()
        layout.add_widget(self.chwazi)

        back_btn = KButton(text=translations[current_language]['back'], size_hint=(1, None), height=60)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.transition.direction = 'down'
        self.manager.current = 'start'
        self.chwazi.player_circles = {}
        self.chwazi.teams_assigned = False
        self.chwazi.clear_widgets()

class BelotApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition(duration=0.25))
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(BelotGameScreen(name='game'))
        sm.add_widget(ChwaziScreen(name='chwazi'))
        return sm

    def switch_language(self):
        global current_language
        current_language = 'bg' if current_language == 'en' else 'en'
        self.root.get_screen('start').refresh_texts()
        self.root.get_screen('game').refresh_texts()
        self.root.get_screen('chwazi').children[0].children[0].text = translations[current_language]['back']

if __name__ == '__main__':
    BelotApp().run()
