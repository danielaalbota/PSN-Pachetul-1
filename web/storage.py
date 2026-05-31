import json
import os
from datetime import datetime

# Fișierele unde salvăm datele (simulează EEPROM)
MESSAGES_FILE = 'messages.json'
FLOODS_FILE = 'floods.json'

# Numărul maxim de mesaje/evenimente salvate
MAX_ITEMS = 10


# ──────────────────────────────────────────
#  FUNCȚII PENTRU MESAJE
# ──────────────────────────────────────────

def load_messages():
    """Citește mesajele salvate din fișier."""
    if not os.path.exists(MESSAGES_FILE):
        return []
    with open(MESSAGES_FILE, 'r') as f:
        return json.load(f)


def save_message(text):
    """Salvează un mesaj nou. Dacă sunt deja 10, îl șterge pe cel mai vechi."""
    messages = load_messages()

    new_message = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),  # ID unic bazat pe timp
        'text': text,
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }

    messages.append(new_message)

    # Păstrăm doar ultimele 10
    if len(messages) > MAX_ITEMS:
        messages = messages[-MAX_ITEMS:]

    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)


# ──────────────────────────────────────────
#  FUNCȚII PENTRU EVENIMENTE INUNDAȚII
# ──────────────────────────────────────────

def load_floods():
    """Citește evenimentele de inundații salvate."""
    if not os.path.exists(FLOODS_FILE):
        return []
    with open(FLOODS_FILE, 'r') as f:
        return json.load(f)


def save_flood_event(sensor_value):
    """Salvează un eveniment de inundație nou."""
    floods = load_floods()

    new_event = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'sensor_value': sensor_value,
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }

    floods.append(new_event)

    # Păstrăm doar ultimele 10
    if len(floods) > MAX_ITEMS:
        floods = floods[-MAX_ITEMS:]

    with open(FLOODS_FILE, 'w') as f:
        json.dump(floods, f, indent=2)


def delete_flood_event(event_id):
    """Șterge un eveniment de inundație după ID-ul lui."""
    floods = load_floods()
    floods = [f for f in floods if f['id'] != event_id]

    with open(FLOODS_FILE, 'w') as f:
        json.dump(floods, f, indent=2)