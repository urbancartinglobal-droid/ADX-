import pygame
import pyaudio
import struct
import threading
import os
import sys
import platform
import cv2
from PIL import Image, ImageSequence
import datetime
import subprocess
import time

script_dir = os.path.dirname(__file__)
ADX_MUG_MODE = os.getenv("ADX_MUG_MODE", "0") == "1"

grab_active = False

CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_CYAN = (0, 200, 200)
DARK_BLUE = (10, 20, 40)
PURPLE = (155, 124, 255)
AMBER = (240, 173, 91)
PANEL = (13, 18, 26)
MUTED = (137, 147, 166)
HIGHLIGHT_ALPHA = 80

pygame.init()

def get_font_path():
    system = platform.system()
    if system == "Darwin":
        return "Orbitron-VariableFont_wght.ttf"
    return None

font_path = get_font_path()
if font_path and os.path.exists(font_path):
    clock_font = pygame.font.Font(font_path, 72)
    clock_shadow_font = pygame.font.Font(font_path, 72)
    description_font = pygame.font.Font(font_path, 16)
    todo_font = pygame.font.Font(font_path, 28)
else:
    clock_font = pygame.font.SysFont("Arial", 72, bold=True)
    clock_shadow_font = pygame.font.SysFont("Arial", 72, bold=True)
    description_font = pygame.font.SysFont("Arial", 16)
    todo_font = pygame.font.SysFont("Arial", 28)
track_font = pygame.font.SysFont("Arial", 26)

todo_file_path = ".todo.txt"
pico_description_lines = [
    "ADX Personal AI Assistant",
    "Personality is stable, but can be customized",
    "Voice-enabled desktop automation",
    "Modular and extensible architecture",
    "Supports system, file and productivity tools",
    "Designed for personal projects and experimentation",
]

screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("ADXmug — Intelligence Command Center" if ADX_MUG_MODE else "ADX")

def load_image_safe(path, default_size=(200, 200)):
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, default_size)
        except Exception:
            pass
    surf = pygame.Surface(default_size)
    surf.fill(CYAN)
    return surf

def load_gif_safe(gif_path, fallback_frames=10):
    try:
        gif = Image.open(gif_path)
        frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(gif)]
        return [pygame.image.frombuffer(frame.tobytes(), frame.size, "RGBA") for frame in frames]
    except Exception:
        frames = []
        size = (200, 200)
        for i in range(fallback_frames):
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.circle(surf, CYAN, (size[0] // 2, size[1] // 2), 50 + i * 2)
            frames.append(surf)
        return frames

gif_path = os.path.join(script_dir, "im.gif")
pico_gif_path = os.path.join(script_dir, "picogram.gif")
frame_surfaces = load_gif_safe(gif_path)
pico_surfaces = load_gif_safe(pico_gif_path)

p = None
stream = None
def init_audio():
    global p, stream
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=512)
        return True
    except Exception:
        print("Audio input not available, running without microphone")
        return False

audio_available = init_audio()

def get_volume(data):
    if not data:
        return 0
    count = len(data) // 2
    shorts = struct.unpack(f"%dh" % count, data)
    return (sum(s ** 2 for s in shorts) / count) ** 0.5

def load_todo_tasks():
    if os.path.exists(todo_file_path):
        try:
            with open(todo_file_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except Exception:
            pass
    return []

track = ""
track_lock = threading.Lock()

def fetch_track():
    global track
    try:
        system = platform.system()
        if system == "Darwin":
            running = subprocess.check_output('ps -ef | grep "MacOS/Spotify" | grep -v "grep" | wc -l', shell=True, text=True).strip()
            if running == "0":
                new_track = ""
            else:
                new_track = subprocess.check_output("""osascript -e 'tell application "Spotify"
                    set t to current track
                    return artist of t & " - " & name of t
                    end tell'""", shell=True, text=True).strip()
        else:
            new_track = ""
    except Exception:
        new_track = ""
    with track_lock:
        track = new_track

def toggle_fullscreen(screen):
    global screen_width, screen_height
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    return pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

def _text(surface, text, x, y, size=16, color=WHITE, bold=False):
    font = pygame.font.SysFont("Arial", size, bold=bold)
    surface.blit(font.render(text, True, color), (x, y))

def _panel(surface, rect, accent):
    pygame.draw.rect(surface, PANEL, rect, border_radius=8)
    pygame.draw.rect(surface, accent, rect, width=1, border_radius=8)
    pygame.draw.line(surface, accent, (rect.left + 1, rect.top + 2), (rect.right - 1, rect.top + 2), 2)

def draw_adxmug_dashboard(surface):
    """Reference-inspired ADXmug Command Center rendered inside the ADX UI."""
    w, h = surface.get_size()
    surface.fill(BLACK)
    margin = max(18, int(w * 0.025))
    scale = max(0.72, min(1.25, w / 1200))

    _text(surface, "ADXmug", margin, 20, int(24 * scale), WHITE, True)
    _text(surface, "● SYSTEMS ACTIVE  ·  24/7  ·  CORPORATE  ·  MACRO  ·  GLOBAL", margin + int(110 * scale), 28, int(10 * scale), LIGHT_CYAN)
    now = datetime.datetime.now()
    _text(surface, now.strftime("%d %b %Y  ·  %H:%M:%S"), max(margin, w - 190), 27, 10, MUTED)

    _text(surface, "The intelligence layer behind your decisions.", margin, 70, int(28 * scale), WHITE, True)
    _text(surface, "Everything that happens  →  filtered signals  →  business impact  →  sector opportunity", margin, 108, int(12 * scale), MUTED)

    gap = 12
    top = 150
    card_w = (w - 2 * margin - 2 * gap) // 3
    card_h = 145
    cards = [
        ("Corporate Intelligence", "INDIA · COMPANY SIGNALS", PURPLE, "Capex · orders · capacity · earnings · filings", "1,240", "SOURCES", "7", "SIGNALS"),
        ("Macro Intelligence", "INDIA · GOVERNMENT", CYAN, "RBI · ministries · policy · PLI · procurement", "54", "SOURCES", "4", "SIGNALS"),
        ("Global Intelligence", "WORLD → INDIA", AMBER, "Rates · trade · commodities · global spillovers", "212", "SOURCES", "5", "SIGNALS"),
    ]
    for i, (title, sub, accent, body, v1, n1, v2, n2) in enumerate(cards):
        r = pygame.Rect(margin + i * (card_w + gap), top, card_w, card_h)
        _panel(surface, r, accent)
        _text(surface, title, r.x + 15, r.y + 14, int(16 * scale), accent, True)
        _text(surface, sub, r.x + 15, r.y + 38, int(8 * scale), MUTED)
        _text(surface, body, r.x + 15, r.y + 67, int(10 * scale), WHITE)
        _text(surface, "24/7", r.x + 15, r.y + 104, int(13 * scale), WHITE, True)
        _text(surface, "ON DUTY", r.x + 15, r.y + 122, int(7 * scale), MUTED)
        _text(surface, v1, r.x + card_w // 2, r.y + 104, int(13 * scale), WHITE, True)
        _text(surface, n1, r.x + card_w // 2, r.y + 122, int(7 * scale), MUTED)
        _text(surface, v2, r.x + int(card_w * .78), r.y + 104, int(13 * scale), WHITE, True)
        _text(surface, n2, r.x + int(card_w * .78), r.y + 122, int(7 * scale), MUTED)

    feed_y = top + card_h + 20
    _text(surface, "THE PIPELINE", margin, feed_y, 9, MUTED, True)
    _text(surface, "From everything that happens, to the few stories that matter.", margin, feed_y + 20, int(20 * scale), WHITE, True)
    _text(surface, "LIVE ACTIVITY — ALL UNITS", margin, feed_y + 58, 9, MUTED, True)

    feed = pygame.Rect(margin, feed_y + 82, w - 2 * margin, max(150, h - feed_y - 190))
    _panel(surface, feed, (45, 51, 66))
    entries = [
        ("MACRO", CYAN, "Ministry / policy signal detected — mapping affected industries"),
        ("CORP", PURPLE, "Corporate filing cluster — checking earnings impact"),
        ("GLOBAL", AMBER, "Trade / commodity signal — India impact pending"),
        ("FILTER", WHITE, "Low-impact duplicate discarded"),
        ("ADX", CYAN, "7DIO.EL opportunity pipeline ready"),
    ]
    yy = feed.y + 18
    for unit, accent, msg in entries:
        _text(surface, f"{unit:<7}", feed.x + 16, yy, 9, accent, True)
        _text(surface, msg, feed.x + 80, yy, 10, MUTED)
        yy += 28

    bottom_y = h - 70
    _panel(surface, pygame.Rect(margin, bottom_y, w - 2 * margin, 48), (45, 51, 66))
    _text(surface, "ASK ADX", margin + 14, bottom_y + 10, 8, MUTED, True)
    _text(surface, '"अभी कौन-सी industry में opportunity है?"', margin + 85, bottom_y + 8, 12, WHITE, True)
    _text(surface, "M = normal ADX UI", max(margin + 350, w - 180), bottom_y + 11, 8, MUTED)

def main():
    global screen, grab_active
    running = True
    fullscreen = False
    frame_idx = 0
    pico_idx = 0
    gif_scale = 1.0
    clock = pygame.time.Clock()
    track_update_ms = 3000
    last_track_ms = 0
    pico_x = None
    pico_y = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = toggle_fullscreen(screen)
                    else:
                        screen = pygame.display.set_mode((1100, 700), pygame.RESIZABLE)
                elif event.key == pygame.K_m and not ADX_MUG_MODE:
                    # Open a separate ADXmug instance without changing the main UI.
                    env = os.environ.copy()
                    env["ADX_MUG_MODE"] = "1"
                    subprocess.Popen([sys.executable, os.path.abspath(__file__)], env=env)

        if ADX_MUG_MODE:
            draw_adxmug_dashboard(screen)
            pygame.display.flip()
            clock.tick(10)
            continue

        try:
            if audio_available and stream:
                audio_data = stream.read(2048, exception_on_overflow=False)
                volume = get_volume(audio_data)
                scale_factor = 1 + min(volume / 1000, 1)
                gif_scale = 0.9 * gif_scale + 0.1 * scale_factor
            else:
                gif_scale *= 0.99
        except Exception:
            pass

        now_ms = pygame.time.get_ticks()
        if now_ms - last_track_ms >= track_update_ms:
            threading.Thread(target=fetch_track, daemon=True).start()
            last_track_ms = now_ms

        screen.fill(BLACK)
        gif_width, gif_height = frame_surfaces[0].get_size()
        scaled_width = int(gif_width * gif_scale)
        scaled_height = int(gif_height * gif_scale)
        adx_frame = frame_surfaces[frame_idx]
        adx_scaled = pygame.transform.scale(adx_frame, (scaled_width, scaled_height)).convert_alpha()
        adx_tint = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        adx_tint.fill(CYAN + (128,))
        adx_scaled.blit(adx_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        adx_rect = adx_scaled.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(adx_scaled, adx_rect)

        pico_frame = pico_surfaces[pico_idx]
        pico_target_width = 600
        pico_scale = pico_target_width / pico_frame.get_width()
        pico_target_height = int(pico_frame.get_height() * pico_scale)
        pico_scaled = pygame.transform.scale(pico_frame, (pico_target_width, pico_target_height)).convert_alpha()
        pico_tint = pygame.Surface((pico_target_width, pico_target_height), pygame.SRCALPHA)
        pico_tint.fill(CYAN + (128,))
        pico_scaled.blit(pico_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if pico_x is None or pico_y is None:
            pico_x = screen.get_width() - pico_target_width - 200
            pico_y = screen.get_height() - pico_target_height - 100
        screen.blit(pico_scaled, (int(pico_x), int(pico_y)))

        line_spacing = 6
        text_margin = 80
        for i, line in enumerate(pico_description_lines):
            line_surface = description_font.render(line, True, LIGHT_CYAN)
            line_x = int(pico_x) + text_margin
            line_y = int(pico_y) + pico_target_height + 10 + i * (line_surface.get_height() + line_spacing)
            screen.blit(line_surface, (line_x, line_y))

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %B %d, %Y")
        time_shadow = clock_shadow_font.render(current_time, True, BLACK)
        screen.blit(time_shadow, time_shadow.get_rect(center=(screen.get_width() // 2 + 3, 103)))
        time_surface = clock_font.render(current_time, True, CYAN)
        screen.blit(time_surface, time_surface.get_rect(center=(screen.get_width() // 2, 100)))
        date_surface = pygame.font.SysFont("Arial", 24, bold=True).render(date_str, True, WHITE)
        screen.blit(date_surface, date_surface.get_rect(center=(screen.get_width() // 2, 140)))

        with track_lock:
            current_track = track
        if current_track:
            track_surface = track_font.render(current_track, True, LIGHT_CYAN)
            screen.blit(track_surface, (20, screen.get_height() - track_surface.get_height() - 20))

        todo_tasks = load_todo_tasks()
        todo_x, todo_y = 40, 200
        todo_spacing = 28
        for i, task in enumerate(todo_tasks[:8]):
            todo_surface = todo_font.render(task, True, LIGHT_CYAN)
            screen.blit(todo_surface, (todo_x, todo_y + i * todo_spacing))

        pygame.display.flip()
        frame_idx = (frame_idx + 1) % len(frame_surfaces)
        pico_idx = (pico_idx + 1) % len(pico_surfaces)
        clock.tick(30)

    if stream:
        stream.stop_stream()
        stream.close()
    if p:
        p.terminate()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
