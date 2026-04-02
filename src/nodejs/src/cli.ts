#!/usr/bin/env node
/**
 * WinUIDevKit CLI for Node.js — init / run / build commands.
 */

import { Command } from "commander";
import * as fs from "fs";
import * as path from "path";
import { execSync } from "child_process";

const program = new Command();

program.name("winui").description("WinUIDevKit Node.js CLI").version("0.1.0");

program
  .command("init <name>")
  .description("Scaffold a new WinUI3 Node.js project")
  .action((name: string) => {
    const dir = path.resolve(name);
    fs.mkdirSync(path.join(dir, "app"), { recursive: true });

    // package.json
    fs.writeFileSync(
      path.join(dir, "package.json"),
      JSON.stringify(
        {
          name: name.toLowerCase(),
          version: "0.1.0",
          main: "app/main.ts",
          scripts: { start: "npx ts-node app/main.ts" },
          dependencies: { winuidevkit: "^0.1.0" },
        },
        null,
        2
      )
    );

    // MainWindow.xaml
    fs.writeFileSync(
      path.join(dir, "app", "MainWindow.xaml"),
      `<Window
  xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  Title="${name}">
  <StackPanel HorizontalAlignment="Center" VerticalAlignment="Center">
    <TextBlock x:Name="greeting" Text="Hello from WinUI3 + Node.js!" FontSize="24"/>
    <Button x:Name="myButton" Content="Click me"/>
  </StackPanel>
</Window>
`
    );

    // main.ts
    fs.writeFileSync(
      path.join(dir, "app", "main.ts"),
      `import { WinUIApp } from "winuidevkit";

const app = new WinUIApp("app/MainWindow.xaml");

app.on("myButton.Click", (sender: any, args: any) => {
  const greeting = app.find("greeting");
  greeting.Text = "Button clicked!";
});

app.run();
`
    );

    console.log(`Created ${name}/ — run 'cd ${name} && npm install && npm start'`);
  });

program
  .command("run")
  .description("Run the WinUI3 app in the current directory")
  .action(() => {
    execSync("npx ts-node app/main.ts", { stdio: "inherit", cwd: process.cwd() });
  });

program.parse();
