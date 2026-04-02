/**
 * WinUIDevKit Node.js runtime — wraps the N-API native addon.
 */

import * as path from "path";

// Load the native addon (.node binary built by cmake-js)
const addonPath = path.join(__dirname, "..", "build", "Release", "winuidevkit.node");
const native = require(addonPath);

export class WinUIApp {
  private xamlPath: string;
  private windowHandle: any;
  private eventHandlers: Map<string, Function> = new Map();

  constructor(xamlRelativePath: string) {
    this.xamlPath = path.resolve(xamlRelativePath);
  }

  /** Register event handler: "elementName.EventName" */
  on(key: string, handler: Function): this {
    this.eventHandlers.set(key, handler);
    return this;
  }

  /** Find a named XAML element */
  find(name: string): any {
    if (!this.windowHandle) throw new Error("App not running — call run() first");
    return native.findName(this.windowHandle, name);
  }

  /** Launch the WinUI3 application */
  run(): void {
    // Initialize WinAppSDK bootstrap
    native.initialize();

    // Read XAML and create window
    const fs = require("fs");
    const xamlContent = fs.readFileSync(this.xamlPath, "utf-8");
    const uiElement = native.loadXaml(xamlContent);
    this.windowHandle = native.createWindow(uiElement);

    // Wire event handlers
    // Note: Full implementation would use the native message pump bridge
    // to dispatch events from the UI thread to the Node.js event loop

    // Block on the message loop (runs until window closes)
    // native.runMessageLoop();

    native.shutdown();
  }
}
