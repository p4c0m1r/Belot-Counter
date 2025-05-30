from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout

Window.size = (400, 600)

# Translation dictionary
translations = {
    'en': {
        'title': "Belot Score Counter",
        'start_game': "Start Game",
        'enter_team_a': "Enter Team A Name",
        'enter_team_b': "Enter Team B Name",
        'round': "Round",
        'submit_scores': "Submit Round Scores",
        'undo': "Undo Last Round",
        'restart': "Restart Game",
        'score_error': "Please enter valid numbers.",
        'negative_error': "Scores cannot be negative!",
        'undo_error': "No round to undo.",
        'undo_success': "Last round undone.",
        'team_a_wins': "{} wins!",
        'team_b_wins': "{} wins!",
        'tie': "It's a tie!",
        'game_over': "Game Over!",
        'score_text': "{}: {}  |  {}: {}",
        'lang_toggle': "BG"
    },
    'bg': {
        'title': "Белот Точкова Система",
        'start_game': "Начало на игра",
        'enter_team_a': "Въведете име на отбор A",
        'enter_team_b': "Въведете име на отбор B",
        'round': "Рунд",
        'submit_scores': "Запази резултатите",
        'undo': "Отмени последния рунд",
        'restart': "Рестартирай играта",
        'score_error': "Моля, въведете валидни числа.",
        'negative_error': "Точките не може да са отрицателни!",
        'undo_error': "Няма рунд за отмяна.",
        'undo_success': "Последният рунд е отменен.",
        'team_a_wins': "{} печели!",
        'team_b_wins': "{} печели!",
        'tie': "Равен резултат!",
        'game_over': "Край на играта!",
        'score_text': "{}: {}  |  {}: {}",
        'lang_toggle': "EN"
    }
}

current_language = 'en'

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        self.title_label = Label(font_size='28sp', bold=True, size_hint=(1, 0.2))

        self.team_a_input = TextInput(multiline=False, size_hint=(1, 0.15), font_size='16sp')
        self.team_b_input = TextInput(multiline=False, size_hint=(1, 0.15), font_size='16sp')

        self.start_btn = Button(size_hint=(1, 0.2), font_size='18sp', background_color=(0.1, 0.6, 0.1, 1))
        self.start_btn.bind(on_press=self.start_game)

        self.lang_btn = Button(size_hint=(1, 0.1), font_size='16sp', background_color=(0.3, 0.3, 0.3, 1))
        self.lang_btn.bind(on_press=self.toggle_language)

        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.team_a_input)
        self.layout.add_widget(self.team_b_input)
        self.layout.add_widget(self.start_btn)
        self.layout.add_widget(self.lang_btn)

        self.add_widget(self.layout)
        self.refresh_texts()

    def refresh_texts(self):
        t = translations[current_language]
        self.title_label.text = t['title']
        self.team_a_input.hint_text = t['enter_team_a']
        self.team_b_input.hint_text = t['enter_team_b']
        self.start_btn.text = t['start_game']
        self.lang_btn.text = t['lang_toggle']

    def toggle_language(self, instance):
        App.get_running_app().switch_language()

    def start_game(self, instance):
        team_a = self.team_a_input.text.strip() or "Team A"
        team_b = self.team_b_input.text.strip() or "Team B"
        self.manager.get_screen('game').set_team_names(team_a, team_b)
        self.manager.current = 'game'


class BelotGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team_a_name = "Team A"
        self.team_b_name = "Team B"
        self.team_a_score = 0
        self.team_b_score = 0
        self.round_num = 1
        self.history = []

        root = FloatLayout()

        bg = Image(source='/mnt/data/bce6c46f-1daa-4f72-928f-85c05d2c097e.png',
                   allow_stretch=True, keep_ratio=False,
                   size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        root.add_widget(bg)

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10,
                                size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})

        self.header = Label(font_size='24sp', bold=True, size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.layout.add_widget(self.header)

        self.round_label = Label(font_size='20sp', size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.layout.add_widget(self.round_label)

        input_grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.2))
        self.input_a = TextInput(input_filter='int', multiline=False, font_size='16sp', background_color=(0, 0, 0, 0.5))
        self.input_b = TextInput(input_filter='int', multiline=False, font_size='16sp', background_color=(0, 0, 0, 0.5))
        input_grid.add_widget(self.input_a)
        input_grid.add_widget(self.input_b)
        self.layout.add_widget(input_grid)

        self.submit_btn = Button(size_hint=(1, 0.15), font_size='16sp', background_color=(0.1, 0.4, 0.8, 0.9))
        self.submit_btn.bind(on_press=self.submit_scores)
        self.layout.add_widget(self.submit_btn)

        button_box = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.undo_btn = Button(font_size='14sp', background_color=(0.7, 0.7, 0.1, 0.9))
        self.undo_btn.bind(on_press=self.undo_round)
        self.restart_btn = Button(font_size='14sp', background_color=(0.8, 0.1, 0.1, 0.9))
        self.restart_btn.bind(on_press=self.restart_game)
        button_box.add_widget(self.undo_btn)
        button_box.add_widget(self.restart_btn)
        self.layout.add_widget(button_box)

        self.score_label = Label(font_size='18sp', size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.layout.add_widget(self.score_label)

        self.message_label = Label(font_size='14sp', size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.layout.add_widget(self.message_label)

        root.add_widget(self.layout)
        self.add_widget(root)

        self.refresh_texts()

    def refresh_texts(self):
        t = translations[current_language]
        self.header.text = t['title']
        self.submit_btn.text = t['submit_scores']
        self.undo_btn.text = t['undo']
        self.restart_btn.text = t['restart']
        self.input_a.hint_text = f"{self.team_a_name}"
        self.input_b.hint_text = f"{self.team_b_name}"
        self.update_labels()

    def set_team_names(self, a_name, b_name):
        self.team_a_name = a_name
        self.team_b_name = b_name
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


class BelotApp(App):
    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        self.start_screen = StartScreen(name='start')
        self.game_screen = BelotGameScreen(name='game')
        self.sm.add_widget(self.start_screen)
        self.sm.add_widget(self.game_screen)
        return self.sm

    def switch_language(self):
        global current_language
        current_language = 'bg' if current_language == 'en' else 'en'
        self.start_screen.refresh_texts()
        self.game_screen.refresh_texts()


if __name__ == '__main__':
    BelotApp().run()
