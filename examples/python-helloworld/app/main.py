"""
Python HelloWorld — uses pywinui (pythonnet bridge).
"""
from pywinui_runtime.app import window

click_count = 0

@window("app/MainWindow.xaml", title="HelloWorld")
def main(view):
    pass

def on_clickButton_Click(sender, args):
    global click_count
    click_count += 1
    # Access the counter TextBlock via the view proxy
    sender.GetType()  # keep reference alive
    print(f"Button clicked {click_count} times")

if __name__ == "__main__":
    main()
