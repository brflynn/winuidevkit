"""
Python HelloWorld — uses pywinui (pythonnet bridge).
"""
from pywinui_runtime.app import window

click_count = 0

@window("app/MainWindow.xaml")
class MainWindow:
    def __init__(self, view):
        self.view = view

    def on_clickButton_Click(self, sender, args):
        global click_count
        click_count += 1
        print(f"Button clicked {click_count} times")

if __name__ == "__main__":
    MainWindow.run()
