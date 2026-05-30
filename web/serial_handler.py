import threading
import time

# Încercăm să importăm librăria pentru comunicație serială
# Dacă nu e instalată sau Arduino nu e conectat, folosim modul simulat
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# ──────────────────────────────────────────
#  CONFIGURARE - MODIFICĂ AICI
# ──────────────────────────────────────────

SERIAL_PORT = 'COM3'    # Portul Arduino (COM3, COM4 etc. pe Windows / /dev/ttyUSB0 pe Linux)
BAUD_RATE = 9600        # Viteza de comunicație (trebuie să fie aceeași ca în Arduino)

# ──────────────────────────────────────────
#  VARIABILE GLOBALE
# ──────────────────────────────────────────

arduino = None          # Conexiunea cu Arduino
is_connected = False    # Suntem conectați la Arduino?

# Date simulate (folosite când Arduino nu e conectat)
simulated_data = {
    'temperature': 25.0,
    'led_status': False,
    'flood_detected': False
}


# ──────────────────────────────────────────
#  CONECTARE LA ARDUINO
# ──────────────────────────────────────────

def connect():
    """Încearcă să se conecteze la Arduino."""
    global arduino, is_connected

    if not SERIAL_AVAILABLE:
        print("⚠️  Librăria pyserial nu e instalată. Rulăm în mod simulat.")
        return False

    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Așteptăm să se stabilizeze conexiunea
        is_connected = True
        print(f"✅ Conectat la Arduino pe portul {SERIAL_PORT}")
        return True
    except Exception as e:
        print(f"⚠️  Nu s-a putut conecta la Arduino: {e}")
        print("⚠️  Rulăm în mod simulat.")
        is_connected = False
        return False


# ──────────────────────────────────────────
#  TRIMITERE COMENZI CĂTRE ARDUINO
# ──────────────────────────────────────────

def send_command(command):
    """Trimite o comandă către Arduino (ex: 'A' pentru LED on, 'S' pentru LED off)."""
    global simulated_data

    if is_connected and arduino:
        try:
            arduino.write(command.encode())
            print(f"📤 Comandă trimisă: {command}")
        except Exception as e:
            print(f"❌ Eroare la trimiterea comenzii: {e}")
    else:
        # Mod simulat
        print(f"🔵 [SIMULAT] Comandă trimisă: {command}")
        if command == 'A':
            simulated_data['led_status'] = True
        elif command == 'S':
            simulated_data['led_status'] = False


def send_message(message):
    """Trimite un mesaj text către Arduino."""
    if is_connected and arduino:
        try:
            arduino.write(f"MSG:{message}\n".encode())
            print(f"📤 Mesaj trimis: {message}")
        except Exception as e:
            print(f"❌ Eroare la trimiterea mesajului: {e}")
    else:
        print(f"🔵 [SIMULAT] Mesaj trimis: {message}")


# ──────────────────────────────────────────
#  CITIRE DATE DE LA ARDUINO
# ──────────────────────────────────────────

def get_temperature():
    """Returnează temperatura curentă."""
    if is_connected and arduino:
        try:
            arduino.write(b'T')  # Cerem temperatura
            time.sleep(0.1)
            if arduino.in_waiting:
                line = arduino.readline().decode().strip()
                return float(line)
        except Exception as e:
            print(f"❌ Eroare la citirea temperaturii: {e}")
            return simulated_data['temperature']
    else:
        # Mod simulat - temperatura variază ușor
        simulated_data['temperature'] += 0.1
        if simulated_data['temperature'] > 35:
            simulated_data['temperature'] = 20.0
        return round(simulated_data['temperature'], 1)


def get_led_status():
    """Returnează statusul LED-ului (True = aprins, False = stins)."""
    if is_connected and arduino:
        try:
            arduino.write(b'L')  # Cerem statusul LED-ului
            time.sleep(0.1)
            if arduino.in_waiting:
                line = arduino.readline().decode().strip()
                return line == '1'
        except Exception as e:
            print(f"❌ Eroare la citirea statusului LED: {e}")
            return simulated_data['led_status']
    else:
        return simulated_data['led_status']


def get_flood_status():
    """Returnează dacă e detectată o inundație (True/False)."""
    if is_connected and arduino:
        try:
            arduino.write(b'F')  # Cerem statusul senzorului de inundație
            time.sleep(0.1)
            if arduino.in_waiting:
                line = arduino.readline().decode().strip()
                return line == '1'
        except Exception as e:
            print(f"❌ Eroare la citirea senzorului de inundație: {e}")
            return simulated_data['flood_detected']
    else:
        return simulated_data['flood_detected']


# ──────────────────────────────────────────
#  FUNCȚII PENTRU MOD SIMULAT (TESTARE)
# ──────────────────────────────────────────

def simulate_flood(active=True):
    """Simulează o inundație (doar în mod simulat, pentru testare)."""
    simulated_data['flood_detected'] = active
    print(f"🔵 [SIMULAT] Inundație: {'DETECTATĂ' if active else 'Oprită'}")