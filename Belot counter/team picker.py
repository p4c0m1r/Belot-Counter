from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation
from random import shuffle
from kivy.uix.widget import Widget


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
    team_colors = [(1, 1, 0), (0.6, 0, 1)]  # Two team colors

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_circles = {}  # touch.uid -> PlayerCircle
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
