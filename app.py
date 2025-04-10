from textual.app import App
from screens.session import SessionScreen


class Noni(App):

    # Session screen will always be the first screen on launch
    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        self.push_screen(SessionScreen())


if __name__ == "__main__":
    app = Noni()
    app.run()
