from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

Window.size = (400, 600)


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        layout.add_widget(Label(text="Belot Score Counter", font_size='24sp', size_hint=(1, 0.2)))

        self.team_a_input = TextInput(hint_text="Enter Team A Name", multiline=False)
        self.team_b_input = TextInput(hint_text="Enter Team B Name", multiline=False)

        layout.add_widget(self.team_a_input)
        layout.add_widget(self.team_b_input)

        self.start_btn = Button(text="Start Game", size_hint=(1, 0.3))
        self.start_btn.bind(on_press=self.start_game)
        layout.add_widget(self.start_btn)

        self.add_widget(layout)

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

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.header = Label(text='Belot Score Counter', font_size='22sp', size_hint=(1, 0.1))
        self.layout.add_widget(self.header)

        self.round_label = Label(text=f"Round {self.round_num}", font_size='18sp', size_hint=(1, 0.1))
        self.layout.add_widget(self.round_label)

        input_grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.2))

        self.input_a = TextInput(hint_text='Enter score for Team A', input_filter='int', multiline=False)
        self.input_b = TextInput(hint_text='Enter score for Team B', input_filter='int', multiline=False)

        input_grid.add_widget(self.input_a)
        input_grid.add_widget(self.input_b)
        self.layout.add_widget(input_grid)

        self.submit_btn = Button(text='Submit Round Scores', size_hint=(1, 0.15))
        self.submit_btn.bind(on_press=self.submit_scores)
        self.layout.add_widget(self.submit_btn)

        button_box = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.undo_btn = Button(text='Undo Last Round')
        self.undo_btn.bind(on_press=self.undo_round)

        self.restart_btn = Button(text='Restart Game')
        self.restart_btn.bind(on_press=self.restart_game)

        button_box.add_widget(self.undo_btn)
        button_box.add_widget(self.restart_btn)
        self.layout.add_widget(button_box)

        self.score_label = Label(text=self.get_score_text(), font_size='16sp', size_hint=(1, 0.1))
        self.layout.add_widget(self.score_label)

        self.message_label = Label(text='', font_size='14sp', size_hint=(1, 0.1))
        self.layout.add_widget(self.message_label)

        self.add_widget(self.layout)

    def set_team_names(self, a_name, b_name):
        self.team_a_name = a_name
        self.team_b_name = b_name
        self.update_labels()

    def get_score_text(self):
        return f"{self.team_a_name}: {self.team_a_score}  |  {self.team_b_name}: {self.team_b_score}"

    def update_labels(self):
        self.round_label.text = f"Round {self.round_num}"
        self.score_label.text = self.get_score_text()

    def submit_scores(self, instance):
        try:
            a_points = int(self.input_a.text)
            b_points = int(self.input_b.text)
        except ValueError:
            self.message_label.text = "Please enter valid numbers."
            return

        if a_points < 0 or b_points < 0:
            self.message_label.text = "Scores cannot be negative!"
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
                self.message_label.text = f"{self.team_a_name} wins!"
            elif self.team_b_score > self.team_a_score:
                self.message_label.text = f"{self.team_b_name} wins!"
            else:
                self.message_label.text = "It's a tie!"
            self.round_label.text = "Game Over!"

    def undo_round(self, instance):
        if not self.history:
            self.message_label.text = "No round to undo."
            return
        self.team_a_score, self.team_b_score, self.round_num = self.history.pop()
        self.update_labels()
        self.message_label.text = "Last round undone."
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
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(BelotGameScreen(name='game'))
        return sm


if __name__ == '__main__':
    BelotApp().run()
