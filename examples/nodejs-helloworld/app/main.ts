/**
 * Node.js HelloWorld — uses WinUIDevKit N-API addon.
 */
import { WinUIApp } from "winuidevkit";

let clickCount = 0;
const app = new WinUIApp("app/MainWindow.xaml");

app.on("clickButton.Click", (sender: any, args: any) => {
  clickCount++;
  const counter = app.find("counter");
  counter.Text = `Clicks: ${clickCount}`;
});

app.run();
