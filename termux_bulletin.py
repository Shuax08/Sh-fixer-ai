import os
import sys
import select
import termios
import tty
import random
import asyncio
import requests
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def fetch_news():
    """Fetches latest real-time headlines without caching"""
    try:
        # Latest Live News Topics
        topics = ["WORLD", "NATION", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE"]
        selected_topic = random.choice(topics)
        
        url = f"https://news.google.com/rss/headlines/section/topic/{selected_topic}?hl=en-IN&gl=IN&ceid=IN:en"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        # Cache bypass Parameter
        res = requests.get(f"{url}&t={random.randint(1, 100000)}", headers=headers, timeout=5)
        
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            items = []
            for item in root.findall('.//item'):
                title = item.find('title').text
                # Cleanup publisher name from title if needed
                items.append(title)
            
            # Shuffle to get fresh random order
            random.shuffle(items)
            return items[:10]
    except Exception:
        pass
    return []

def translate_text(text, target_lang):
    try:
        lang_pair = f"en|{target_lang}"
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text)}&langpair={lang_pair}"
        res = requests.get(url, timeout=5).json()
        translated = res.get("responseData", {}).get("translatedText", "")
        if translated and "QUERY LENGTH LIMIT EXCEEDED" not in translated:
            return translated
    except Exception:
        pass
    return text

def get_key_non_blocking():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
            return key.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

async def play_audio(text, voice):
    output_file = "temp_news.mp3"
    if os.path.exists(output_file):
        os.remove(output_file)

    clean_text = text.replace("'", "").replace('"', '').replace('\n', ' ')
    cmd_gen = f'edge-tts --voice {voice} --text "{clean_text}" --write-media {output_file} > /dev/null 2>&1'
    os.system(cmd_gen)
    
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        proc = await asyncio.create_subprocess_shell(
            f"mpv --really-quiet {output_file}",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        return proc
    return None

def make_dashboard(lang_name, text, idx, total_news):
    header_table = Table.grid(expand=True)
    header_table.add_column(justify="center")
    header_table.add_row("[bold cyan]═══ LIVE AI FRESH NEWS BROADCAST ═══[/bold cyan]")
    
    cmd_table = Table(show_header=True, header_style="bold magenta", expand=True, border_style="dim white")
    cmd_table.add_column("Key", style="bold yellow", justify="center", width=10)
    cmd_table.add_column("Action Control", style="bold cyan")
    cmd_table.add_row("n", "Next Language/News")
    cmd_table.add_row("s", "Stop Audio")
    cmd_table.add_row("q", "Quit Radio")

    news_panel = Panel(
        Text(f"\n{text}\n", style="bold white", justify="left"),
        title=f"[bold green] ● LIVE BROADCAST ({lang_name.upper()}) [/bold green]",
        subtitle=f"[bold yellow] Headline {idx+1} of {total_news} [/bold yellow]",
        border_style="bright_blue",
        padding=(1, 2)
    )

    status_panel = Panel(
        f"[bold green]🔊 Reading {lang_name} Text...[/bold green]",
        border_style="dim green"
    )

    console.clear()
    console.print(Panel(header_table, border_style="cyan"))
    console.print(news_panel)
    console.print(cmd_table)
    console.print(status_panel)

async def process_language(lang_name, text, voice, idx, total_news):
    make_dashboard(lang_name, text, idx, total_news)

    proc = await play_audio(text, voice)
    if not proc:
        await asyncio.sleep(2)
        return 'next'

    while proc.returncode is None:
        key = get_key_non_blocking()
        if key == 'n':
            proc.terminate()
            return 'next'
        elif key == 's':
            proc.terminate()
            return 'stop'
        elif key == 'q':
            proc.terminate()
            return 'quit'
        
        await asyncio.sleep(0.1)

    return 'next'

async def main_bulletin():
    news_list = fetch_news()
    if not news_list:
        console.print("[bold red]Failed to load fresh news. Check internet connection![/bold red]")
        return

    voices = {
        "English": "en-US-AnaNeural",
        "Malayalam": "ml-IN-SobhanaNeural",
        "Hindi": "hi-IN-SwaraNeural"
    }

    idx = 0
    while idx < len(news_list):
        title_en = news_list[idx]
        
        # English
        status = await process_language("English", title_en, voices["English"], idx, len(news_list))
        if status == 'quit': break
        if status == 'stop':
            idx += 1
            continue

        # Malayalam
        title_ml = translate_text(title_en, 'ml')
        status = await process_language("Malayalam", title_ml, voices["Malayalam"], idx, len(news_list))
        if status == 'quit': break
        if status == 'stop':
            idx += 1
            continue

        # Hindi
        title_hi = translate_text(title_en, 'hi')
        status = await process_language("Hindi", title_hi, voices["Hindi"], idx, len(news_list))
        if status == 'quit': break
        if status == 'stop':
            idx += 1
            continue

        idx += 1

if __name__ == '__main__':
    try:
        asyncio.run(main_bulletin())
    except KeyboardInterrupt:
        os.system("pkill -f mpv > /dev/null 2>&1")
