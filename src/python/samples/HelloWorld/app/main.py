"""Code-behind for MainWindow – HelloWorld sample."""


class MainWindow:
    """Handles UI logic for the main window.

    ``view`` is a ViewProxy exposing all x:Name elements as attributes:
      - view.titleText
      - view.statusText
      - view.helloButton
      - view.dialogButton
    """

    def __init__(self, view):
        self.view = view
        self._clicked = False

    # Convention: on_<x:Name>_<EventName>
    # Automatically wired by pywinui_runtime.binder.wire_events
    def on_helloButton_Click(self, sender, args):
        """Toggle the button text between 'Click me' and 'Clicked!'."""
        if not self._clicked:
            sender.Content = "Clicked!"
            self.view.statusText.Text = "You clicked the button!"
            self._clicked = True
        else:
            sender.Content = "Click me"
            self.view.statusText.Text = "Press the button below"
            self._clicked = False

    def on_dialogButton_Click(self, sender, args):
        """Open a ContentDialog from code-behind."""
        from Microsoft.UI.Xaml.Controls import ContentDialog, ContentDialogButton

        dialog = ContentDialog()
        dialog.Title = "Hello from pywinui!"
        dialog.Content = "This is a WinUI3 ContentDialog opened from Python."
        dialog.PrimaryButtonText = "Nice!"
        dialog.CloseButtonText = "Close"
        dialog.DefaultButton = ContentDialogButton.Primary

        # XamlRoot is required for ContentDialog in WinUI3
        dialog.XamlRoot = self.view.root.XamlRoot

        dialog.ShowAsync()
