# Osu! Reco (Archived)

Osu! Reco is an open-source desktop application that recommends ranked osu! beatmaps based on a player’s global rank and selected game mode.

Instead of relying on a simple logarithmic approximation, the application uses a custom piecewise difficulty model designed to better reflect real player progression. Beatmaps are fetched directly from the official osu! API v2 and displayed in a clean, card-based interface with cover images.

There are many issues with this app since I'm new to python, feel free to help out and teach me more. 

---

## Features

- Rank-based difficulty recommendation using a custom piecewise model
- Supports all osu! game modes:
  - osu!
  - Taiko
  - Catch the Beat
  - osu!mania
- Live beatmap search via the official osu! API v2
- Card-based UI with beatmap covers
- Select beatmaps inside the app and open them in the browser
- Guardrails to prevent excessive API calls and UI freezes
- Custom dark theme using CustomTkinter
- Cross-platform (Windows, macOS, Linux)
- Fully open-source

---

## Requirements

- Python 3.10 or newer
- Internet connection (required for osu! API and cover images)
- Windows, macOS, or Linux

---

## Project Structure

```text
osu-reco/
├── main.py               # Main application and UI logic
├── osu_auth.py           # osu! OAuth token handling
├── osu_pink.json         # CustomTkinter theme
├── config.example.json   # Safe configuration template
├── requirements.txt      # Python dependencies
├── README.md
├── osu_reco.ico          # Application icon
└── .gitignore
```

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/KaneOnPluto/osu-reco.git
cd osu-reco
```
### Step 2: Create a virtual environment (recommended)

```bash
python -m venv venv
```
Activate it:

Windows:

```bash
venv\Scripts\activate
```

MacOS/Linux:

```bash
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### osu! API Setup (Required)

This application uses the official osu! API v2 and requires OAuth credentials.

### Step 4: Create an osu! OAuth application

1. Log in to your osu! account
2. Go to https://osu.ppy.sh/home/account/edit
3. Scroll to the OAuth Applications section
4. Create a new application
5. Set the application type to Confidential
6. The redirect URL is not used and can be set to any valid URL

You will receive:

-> Client ID
-> Client Secret

### Step 3: Create your local config file

Copy the example configuration file:

```bash
cp config.example.json config.json
```
Open config.json and insert your credentials:

```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "access_token": "",
    "token_expiry": 0
}
```

### Running the Application

From the project directory, with your virtual environment activated:

```bash
python main.py
```
The application window should open.






