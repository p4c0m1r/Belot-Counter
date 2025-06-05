from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from random import shuffle
from kivy.core.window import Window

class ChwaziWidget(Widget):
    max_players = 4
    touch_colors = [(1, 0, 0), (0, 1, 0), (0, 0.8, 1), (1, 0.6, 0)]
    player_touches = {}  # uid -> (touch, ellipse, original_color)
    team_colors = [(1, 1, 0), (0.6, 0, 1)]  # Two team colors

    def on_touch_down(self, touch):
        if touch.uid in self.player_touches:
            return
        if len(self.player_touches) >= self.max_players:
            return

        player_index = len(self.player_touches)
        color = self.touch_colors[player_index]

        with self.canvas:
            Color(*color)
            d = 80.
            ellipse = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            self.player_touches[touch.uid] = (touch, ellipse, color)

        if len(self.player_touches) == self.max_players:
            Clock.schedule_once(self.assign_teams, 3)

    def on_touch_up(self, touch):
        if touch.uid in self.player_touches:
            self.canvas.remove(self.player_touches[touch.uid][1])
            del self.player_touches[touch.uid]

    def assign_teams(self, dt):
        if len(self.player_touches) < self.max_players:
            return  # Only assign teams if all 4 are present

        # Shuffle the list of touches
        touches = list(self.player_touches.values())
        shuffle(touches)

        # Assign teams (2 players per team)
        team1 = touches[:2]
        team2 = touches[2:]

        # Assign team colors and redraw
        for team, color in zip([team1, team2], self.team_colors):
            for touch_data in team:
                touch, ellipse, _ = touch_data
                self.canvas.remove(ellipse)
                with self.canvas:
                    Color(*color)
                    d = 100.
                    new_ellipse = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                    self.player_touches[touch.uid] = (touch, new_ellipse, color)


class ChwaziApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return ChwaziWidget()


if __name__ == '__main__':
    ChwaziApp().run()
