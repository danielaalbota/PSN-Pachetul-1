import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ──────────────────────────────────────────
#  CONFIGURARE EMAIL - MODIFICĂ AICI
# ──────────────────────────────────────────

SENDER_EMAIL = "albotadaniela2@gmail.com"       # emailul de pe care trimiți
SENDER_PASSWORD = "mcsb ochg qyaj xwhu"      
RECEIVER_EMAIL = "albotadaniela2@gmail.com"  # emailul unde primești alertele


# ──────────────────────────────────────────
#  FUNCȚIA DE TRIMITERE EMAIL
# ──────────────────────────────────────────

def send_flood_alert(sensor_value):
    """Trimite un email de alertă când se detectează o inundație."""

    # Subiectul emailului
    subject = "⚠️ ALERTĂ INUNDAȚIE DETECTATĂ"

    # Corpul emailului
    body = f"""
    ⚠️ ALERTĂ INUNDAȚIE ⚠️
    
    A fost detectată o inundație la data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    Valoare senzor: {sensor_value}
    
    Verificați sistemul imediat!
    
    -- Sistem automat de monitorizare --
    """

    # Construim emailul
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Trimitem emailul prin Gmail
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
        print("✅ Email de alertă trimis cu succes!")
        return True

    except Exception as e:
        print(f"❌ Eroare la trimiterea emailului: {e}")
        return False