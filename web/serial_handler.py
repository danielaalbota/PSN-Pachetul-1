import threading
import time

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

arduino = None
is_connected = False

simulated_data = {
    'temperature': 25.0,
    'led_status': False,
    'flood_detected': False
}


def connect():
    global arduino, is_connected

    if not SERIAL_AVAILABLE:
        print("⚠️ Librăria pyserial nu e instalată. Rulăm în mod simulat.")
        return False

    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        is_connected = True
        print(f"✅ Conectat la Arduino pe portul {SERIAL_PORT}")
        return True

    except Exception as e:
        print(f"⚠️ Nu s-a putut conecta la Arduino: {e}")
        print("⚠️ Rulăm în mod simulat.")
        is_connected = False
        return False


def send_command(command):
    global simulated_data

    if is_connected and arduino:
        try:
            arduino.write((command + '\n').encode())
            print(f"📤 Comandă trimisă: {command}")

        except Exception as e:
            print(f"❌ Eroare la trimiterea comenzii: {e}")

    else:
        print(f"🔵 [SIMULAT] Comandă trimisă: {command}")

        if command == 'A':
            simulated_data['led_status'] = True

        elif command == 'S':
            simulated_data['led_status'] = False


def send_message(message):
    if is_connected and arduino:
        try:
            arduino.write(f"MSG:{message}\n".encode())
            print(f"📤 Mesaj trimis: {message}")

        except Exception as e:
            print(f"❌ Eroare la trimiterea mesajului: {e}")

    else:
        print(f"🔵 [SIMULAT] Mesaj trimis: {message}")


def get_temperature():
    global simulated_data

    if is_connected and arduino:
        try:
            arduino.reset_input_buffer()

            arduino.write(b'T\n')
            time.sleep(0.2)

            line = arduino.readline().decode().strip()

            if line:
                value = float(line)
                simulated_data['temperature'] = value
                return value

            return simulated_data['temperature']

        except Exception as e:
            print(f"❌ Eroare la citirea temperaturii: {e}")
            return simulated_data['temperature']

    return simulated_data['temperature']


def get_led_status():
    if is_connected and arduino:
        try:
            arduino.write(b'L\n')
            time.sleep(0.1)

            if arduino.in_waiting:
                line = arduino.readline().decode().strip()
                return line == '1'

            return simulated_data['led_status']

        except Exception as e:
            print(f"❌ Eroare la citirea statusului LED: {e}")
            return simulated_data['led_status']

    return simulated_data['led_status']


def get_flood_status():
    if is_connected and arduino:
        try:
            arduino.write(b'F\n')
            time.sleep(0.1)

            if arduino.in_waiting:
                line = arduino.readline().decode().strip()
                return line == '1'

            return simulated_data['flood_detected']

        except Exception as e:
            print(f"❌ Eroare la citirea senzorului de inundație: {e}")
            return simulated_data['flood_detected']

    return simulated_data['flood_detected']


def simulate_flood(active=True):
    simulated_data['flood_detected'] = active
    print(
        f"🔵 [SIMULAT] Inundație: {'DETECTATĂ' if active else 'Oprită'}"
    )