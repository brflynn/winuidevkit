"""Code-behind for MainWindow."""

from pywinui_runtime import window


@window("app/MainWindow.xaml")
class MainWindow:
    def __init__(self, view):
        self.view = view
        self._clicked = False

    def on_helloButton_Click(self, sender, args):
        if not self._clicked:
            sender.Content = "Clicked!"
            self._clicked = True
        else:
            sender.Content = "Click me"
            self._clicked = False


if __name__ == "__main__":
    MainWindow.run()

