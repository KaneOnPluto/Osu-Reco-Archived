import customtkinter as ctk
import requests
import webbrowser
import os
from io import BytesIO
from PIL import Image

from osu_auth import get_access_token

# =================================================
# Constants & Config
# =================================================

MODE_MAP = {
    "osu!": 0,
    "Taiko": 1,
    "Catch the Beat": 2,
    "osu!mania": 3,
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEME_PATH = os.path.join(BASE_DIR, "osu_pink.json")

MAX_RESULTS = 10  # hard UI cap
API_TIMEOUT = 8  # seconds
IMAGE_TIMEOUT = 5  # seconds

selected_map_url = None
selected_card = None

# Difficulty Logic

def rank_to_star_piecewise(rank: int) -> float:
    ranges = [
        (1_000_000, float("inf"), 1.0, 2.5),
        (500_000, 999_999, 2.5, 3.0),
        (350_000, 499_999, 3.0, 3.5),
        (100_000, 349_999, 3.5, 4.5),
        (50_000, 99_999, 5.0, 6.3),
        (10_000, 49_999, 6.3, 7.0),
        (1_000, 9_999, 7.0, 7.8),
        (1, 999, 8.0, 9.5),
    ]

    for r_min, r_max, s_min, s_max in ranges:
        if r_min <= rank <= r_max:
            if r_max == float("inf"):
                return s_min
            t = (rank - r_max) / (r_min - r_max)
            return round(s_min + t * (s_max - s_min), 2)

    return 1.0


def get_star_range(rank: int):
    center = rank_to_star_piecewise(rank)
    return round(center - 0.4, 2), round(center + 0.4, 2)


def update_difficulty_display(rank):
    if not rank:
        difficulty_label.configure(text="Recommended Difficulty: N/A")
        return

    low, high = get_star_range(rank)
    difficulty_label.configure(text=f"Recommended Difficulty: {low}★ – {high}★")


# ==================================================
# osu! API
# ==================================================


def search_beatmaps(star_min, star_max, mode):
    token = get_access_token()

    response = requests.get(
        "https://osu.ppy.sh/api/v2/beatmapsets/search",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "m": mode,
            "status": "ranked",
            "sort": "plays_desc",
            "star": f"{star_min}-{star_max}",
            "limit": MAX_RESULTS,
        },
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("beatmapsets", [])

# UI Helpers 

def load_cover(url):
    try:
        r = requests.get(url, timeout=IMAGE_TIMEOUT)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).resize((80, 80))
        return ctk.CTkImage(img, size=(80, 80))
    except Exception:
        img = Image.new("RGB", (80, 80), "#333333")
        return ctk.CTkImage(img, size=(80, 80))


def create_beatmap_card(parent, bm):
    global selected_card, selected_map_url

    card = ctk.CTkFrame(parent, height=96, corner_radius=12)
    card.pack(fill="x", padx=12, pady=8)

    def select_card():
        global selected_card, selected_map_url

        if selected_card is not None:
            selected_card.configure(border_width=0)

        # Highlight 
        card.configure(border_width=2, border_color="#ff66aa")

        selected_card = card
        selected_map_url = f"https://osu.ppy.sh/beatmapsets/{bm['id']}"

    cover_img = load_cover(bm["covers"]["list@2x"])
    cover = ctk.CTkLabel(card, image=cover_img, text="")
    cover.image = cover_img
    cover.pack(side="left", padx=14, pady=14)

    text_frame = ctk.CTkFrame(card)
    text_frame.pack(side="left", fill="both", expand=True, padx=(4, 12), pady=10)

    title_label = ctk.CTkLabel(
        text_frame,
        text=bm["title"],
        font=("Segoe UI", 14, "bold"),
        anchor="w",
    )
    title_label.pack(anchor="w")

    artist_label = ctk.CTkLabel(
        text_frame,
        text=f"by {bm['artist']}",
        anchor="w",
    )
    artist_label.pack(anchor="w")

    mapper_label = ctk.CTkLabel(
        text_frame,
        text=f"mapped by {bm['creator']}",
        font=("Segoe UI", 11),
        text_color="#aaaaaa",   
        anchor="w",
    )
    mapper_label.pack(anchor="w")

    # ---- Bind selection to ALL widgets ----
    card.bind("<Button-1>", lambda e: select_card())
    cover.bind("<Button-1>", lambda e: select_card())
    text_frame.bind("<Button-1>", lambda e: select_card())
    title_label.bind("<Button-1>", lambda e: select_card())
    artist_label.bind("<Button-1>", lambda e: select_card())
    mapper_label.bind("<Button-1>", lambda e: select_card())


# Results Handling

def display_results(beatmaps):
    global selected_map_url, selected_card
    selected_map_url = None
    selected_card = None

    for widget in results_list.winfo_children():
        widget.destroy()

    if not beatmaps:
        ctk.CTkLabel(
            results_list,
            text="No maps found.",
        ).pack(pady=16)
        return

    for bm in beatmaps[:MAX_RESULTS]:
        create_beatmap_card(results_list, bm)


def on_search_clicked():
    search_button.configure(state="disabled")

    raw = rank_entry.get().replace(",", "").strip()
    try:
        rank = int(raw)
    except ValueError:
        update_difficulty_display(None)
        search_button.configure(state="normal")
        return

    update_difficulty_display(rank)

    star_min, star_max = get_star_range(rank)
    mode = MODE_MAP[mode_dropdown.get()]

    try:
        beatmaps = search_beatmaps(star_min, star_max, mode)
        display_results(beatmaps)
    except Exception as e:
        for widget in results_list.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            results_list,
            text=f"Error: {e}",
        ).pack(pady=16)
    finally:
        search_button.configure(state="normal")


# =================================================
# App UI 
# =================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(THEME_PATH)

app = ctk.CTk()
app.title("Osu! Reco")
app.geometry("760x560")
app.minsize(700, 520)

ICON_PATH = os.path.join(BASE_DIR, "osu_reco.ico")

try:
    app.iconbitmap(ICON_PATH)
except Exception:
    pass  # fails silently on non-Windows platforms

top_frame = ctk.CTkFrame(app)
top_frame.pack(fill="x", padx=24, pady=20)

ctk.CTkLabel(top_frame, text="Rank:").grid(
    row=0, column=0, sticky="w", padx=(0, 8), pady=6
)
rank_entry = ctk.CTkEntry(
    top_frame,
    width=180,
    placeholder_text="e.g. 75000",
)
rank_entry.grid(row=0, column=1, padx=(0, 20), pady=6)

ctk.CTkLabel(top_frame, text="Mode:").grid(
    row=1, column=0, sticky="w", padx=(0, 8), pady=6
)
mode_dropdown = ctk.CTkOptionMenu(
    top_frame,
    values=list(MODE_MAP.keys()),
    width=180,
)
mode_dropdown.grid(row=1, column=1, padx=(0, 20), pady=6)

difficulty_label = ctk.CTkLabel(
    top_frame,
    text="Recommended Difficulty: —",
    font=("Segoe UI", 14, "bold"),
)
difficulty_label.grid(row=2, column=0, columnspan=2, pady=(14, 10))

search_button = ctk.CTkButton(
    top_frame,
    text="Find Maps",
    width=220,
    command=on_search_clicked,
)
search_button.grid(row=3, column=0, columnspan=2, pady=(10, 6))

# --- Results ---
results_frame = ctk.CTkFrame(app)
results_frame.pack(fill="both", expand=True, padx=24, pady=(12, 20))

results_list = ctk.CTkScrollableFrame(results_frame)
results_list.pack(fill="both", expand=True, padx=8, pady=8)


def open_selected_map():
    if selected_map_url:
        webbrowser.open(selected_map_url)


open_button = ctk.CTkButton(
    app,
    text="Open Selected Map in Browser",
    width=260,
    command=open_selected_map,
)
open_button.pack(pady=(0, 18))


app.mainloop()
