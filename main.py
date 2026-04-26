import os
import datetime
import pyautogui
import psutil
import pywhatkit
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

MODEL = "llama3"
SEARCH_DRIVES = ["C:\\", "D:\\", "E:\\"]

def banner():
    console.print(Panel.fit(
        "[bold cyan]ASTRA CLI[/bold cyan]\n"
        "[green]Desktop Assistant[/green]",
        border_style="cyan"
    ))

def ask_llm(prompt):
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": f"""
Convert user text into one command only.

Examples:
open chrome -> open chrome
battery status -> battery
find my report -> find file report

User: {prompt}
Answer:
""",
                "stream": False
            },
            timeout=20
        )

        return r.json()["response"].strip().lower()

    except:
        return prompt.lower()

def smart_find_file(query):
    words = query.lower().split()

    for drive in SEARCH_DRIVES:
        if os.path.exists(drive):
            for root, dirs, files in os.walk(drive):
                for file in files:
                    score = sum(1 for w in words if w in file.lower())
                    if score > 0:
                        return os.path.join(root, file)
    return None

def help_menu():
    table = Table(title="Commands")
    table.add_column("Command")
    table.add_column("Action")

    rows = [
        ("open chrome", "Open browser"),
        ("find file report", "Search file"),
        ("battery", "Battery"),
        ("cpu", "CPU"),
        ("memory", "RAM"),
        ("time", "Current time"),
        ("screenshot", "Take screenshot"),
        ("clear", "Clear"),
        ("exit", "Exit")
    ]

    for r in rows:
        table.add_row(*r)

    console.print(table)

def run_command(cmd):

    if "open chrome" in cmd:
        os.system("start chrome")

    elif "open notepad" in cmd:
        os.system("notepad")

    elif cmd.startswith("search "):
        pywhatkit.search(cmd.replace("search ", ""))

    elif cmd.startswith("youtube "):
        pywhatkit.playonyt(cmd.replace("youtube ", ""))

    elif "find file" in cmd or cmd.startswith("find "):
        q = cmd.replace("find file", "").replace("find", "").strip()
        path = smart_find_file(q)

        if path:
            console.print(f"[green]Found:[/green] {path}")
            os.startfile(path)
        else:
            console.print("[red]No file found[/red]")

    elif cmd == "battery":
        b = psutil.sensors_battery()
        console.print(f"Battery: {b.percent}%")

    elif cmd == "cpu":
        console.print(f"CPU: {psutil.cpu_percent()}%")

    elif cmd == "memory":
        m = psutil.virtual_memory()
        console.print(f"RAM Used: {m.percent}%")

    elif cmd == "time":
        console.print(datetime.datetime.now().strftime("%I:%M %p"))

    elif cmd == "screenshot":
        pyautogui.screenshot().save("astra_shot.png")
        console.print("Saved screenshot")

    elif cmd == "help":
        help_menu()

    elif cmd == "clear":
        os.system("cls")

    elif cmd == "exit":
        raise SystemExit

    else:
        console.print("[red]Unknown command[/red]")

def main():
    banner()

    while True:
        try:
            user = console.input("[bold cyan]AstraCLI > [/bold cyan]")
            cmd = ask_llm(user)
            console.print(f"[green]AI Parsed:[/green] {cmd}")
            run_command(cmd)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
