from flask import Flask, render_template, request, jsonify
import threading
import time

# Importăm modulele noastre
from serial_handler import connect, send_command, send_message, get_temperature, get_led_status, get_flood_status
from storage import save_message, load_messages, save_flood_event, load_floods, delete_flood_event
from email_handler import send_flood_alert

# ──────────────────────────────────────────
#  INIȚIALIZARE FLASK
# ──────────────────────────────────────────

app = Flask(__name__, template_folder='template')

# Variabilă ca să nu trimitem email de mai multe ori pentru același eveniment
flood_alert_sent = False


# ──────────────────────────────────────────
#  MONITORIZARE INUNDAȚII (rulează în fundal)
# ──────────────────────────────────────────

def monitor_floods():
    """Verifică periodic senzorul de inundații și trimite email dacă e cazul."""
    global flood_alert_sent

    while True:
        flood_detected = get_flood_status()

        if flood_detected and not flood_alert_sent:
            print("🚨 INUNDAȚIE DETECTATĂ!")
            sensor_value = 1  # valoare senzor
            save_flood_event(sensor_value)
            send_flood_alert(sensor_value)
            flood_alert_sent = True

        elif not flood_detected:
            flood_alert_sent = False  # resetăm pentru următoarea inundație

        time.sleep(5)  # verificăm la fiecare 5 secunde


# ──────────────────────────────────────────
#  RUTE FLASK (paginile web)
# ──────────────────────────────────────────

@app.route('/')
def index():
    """Pagina principală."""
    return render_template('index.html')


# ── DATE CURENTE ──

@app.route('/api/status')
def get_status():
    """Returnează temperatura și statusul LED-ului ca JSON."""
    return jsonify({
        'temperature': get_temperature(),
        'led_status': get_led_status(),
        'flood_detected': get_flood_status()
    })


# ── CONTROL LED ──

@app.route('/api/led/on', methods=['POST'])
def led_on():
    """Aprinde LED-ul."""
    send_command('A')
    return jsonify({'success': True, 'led_status': True})


@app.route('/api/led/off', methods=['POST'])
def led_off():
    """Stinge LED-ul."""
    send_command('S')
    return jsonify({'success': True, 'led_status': False})


# ── MESAJE ──

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Returnează ultimele 10 mesaje."""
    return jsonify(load_messages())


@app.route('/api/messages', methods=['POST'])
def post_message():
    """Trimite un mesaj nou către Arduino și îl salvează."""
    data = request.get_json()
    text = data.get('message', '').strip()

    if not text:
        return jsonify({'success': False, 'error': 'Mesajul e gol!'}), 400

    send_message(text)
    save_message(text)
    return jsonify({'success': True})


# ── EVENIMENTE INUNDAȚII ──

@app.route('/api/floods', methods=['GET'])
def get_floods():
    """Returnează ultimele 10 evenimente de inundații."""
    return jsonify(load_floods())


@app.route('/api/floods/<event_id>', methods=['DELETE'])
def delete_flood(event_id):
    """Șterge un eveniment de inundație după ID."""
    delete_flood_event(event_id)
    return jsonify({'success': True})


# ──────────────────────────────────────────
#  PORNIRE APLICAȚIE
# ──────────────────────────────────────────

if __name__ == '__main__':
    # Conectăm la Arduino
    connect()

    # Pornim monitorizarea inundațiilor într-un thread separat
    flood_thread = threading.Thread(target=monitor_floods, daemon=True)
    flood_thread.start()

    # Pornim serverul Flask
    print("🚀 Server pornit! Deschide http://localhost:5000 în browser.")
    app.run(debug=True, use_reloader=False)