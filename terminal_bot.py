import os
import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.theme import Theme
from rich.align import Align
from google import genai
from google.genai import types

CREATOR_NAME = "Shuax"
YOUTUBE_URL = "https://youtube.com/@shuaxmods133?si=XWLeUx-xCkz1QwVu"
INSTAGRAM_URL = "https://www.instagram.com/shuaaaaaib?igsi=am4xaWF0bTdmeGo4"

custom_theme = Theme({
    "user": "bold cyan",
    "bot": "bold bright_green",
    "banner": "bold bright_magenta",
    "accent": "bold yellow",
    "error": "bold red"
})

console = Console(theme=custom_theme)

# Load API Key safely from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    console.print("[error]Error: GEMINI_API_KEY variable set ചെയ്തിട്ടില്ല![/error]")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

def open_url(url):
    try:
        subprocess.run(["termux-open-url", url])
    except Exception:
        console.print(f"[accent]Link open aayillel ithu copy cheyyu: {url}[/accent]")

def start_styled_terminal_bot():
    console.clear()
    
    banner_text = r"""
  ██████╗ ██╗  ██╗    ██████╗██╗██╗  ██╗███████╗██████╗ 
  ██╔════╝ ██║  ██║    ██╔════╝██║╚██╗██╔╝██╔════╝██╔══██╗
  ███████╗ ███████║    █████╗  ██║ ╚███╔╝ █████╗  ██████╔╝
  ╚════██║ ██╔══██║    ██╔══╝  ██║ ██╔██╗ ██╔══╝  ██╔══██╗
  ██████╔╝ ██║  ██║    ██║     ██║██╔╝ ██╗███████╗██║  ██║
  ╚═════╝  ╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """
    
    console.print(Align.center(Text(banner_text, style="banner")))
    
    header = Panel(
        Align.center(
            f"[bold cyan]⚡ SH-FIXER-AI TERMINAL ASSISTANT ⚡[/bold cyan]\n"
            f"[dim white]Developed by [/dim white][bold yellow]{CREATOR_NAME}[/bold yellow] [dim white]| System Status: [/dim white][bold green]Online●[/bold green]"
        ),
        border_style="bright_cyan",
        subtitle="[bold dim white]v2.5 Boxed UI[/bold dim white]",
        subtitle_align="right"
    )
    console.print(header)
    console.print()

    yt_choice = console.input("[accent]🔴 Subscribe Shuax's YouTube Channel? (y/n): [/accent]").strip().lower()
    if yt_choice == 'y':
        console.print("[bot]Opening YouTube...[/bot]")
        open_url(YOUTUBE_URL)
        
    insta_choice = console.input("[accent]📸 Follow Shuax on Instagram? (y/n): [/accent]").strip().lower()
    if insta_choice == 'y':
        console.print("[bot]Opening Instagram...[/bot]")
        open_url(INSTAGRAM_URL)

    console.print("\n[dim yellow]💡 Type 'exit' to close Sh-fixer-ai.[/dim yellow]\n")
    console.print("─" * console.width, style="dim white")
    
    config = types.GenerateContentConfig(
        system_instruction=(
            f"Your name is Sh-fixer-ai. You were created by {CREATOR_NAME}. "
            f"When users ask who created you or to introduce yourself, mention that you were created by {CREATOR_NAME}. "
            f"You are a powerful, helpful terminal AI assistant."
        )
    )
    
    chat = client.chats.create(model="gemini-3.6-flash", config=config)
    
    while True:
        try:
            user_input = console.input("\n[user]👤 YOU ❯ [/user]")
            
            if user_input.lower().strip() in ['exit', 'quit', 'bye']:
                console.print("\n[bot]🤖 SH-FIXER-AI ❯ Powering down... Goodbye![/bot]\n")
                break
                
            if not user_input.strip():
                continue

            response = chat.send_message(user_input)
            
            console.print(
                Panel(
                    Markdown(response.text),
                    title="[bold bright_green]🤖 SH-FIXER-AI[/bold bright_green]",
                    title_align="left",
                    border_style="bright_green",
                    padding=(1, 2)
                )
            )
            
        except KeyboardInterrupt:
            console.print("\n[error]Session terminated.[/error]")
            break
        except Exception as e:
            console.print(f"\n[error]Error: {e}[/error]\n")

if __name__ == '__main__':
    start_styled_terminal_bot()
