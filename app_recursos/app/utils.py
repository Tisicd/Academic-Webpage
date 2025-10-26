from flask_mail import Message
from flask import render_template
from . import mail, app
import smtplib

def enviar_correo_confirmacion(email, nombre):
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("Error: No se ha configurado el correo o la contraseña SMTP.")
        return False
    
    try:
        msg = Message(
            subject='Confirmación de Registro - UCE',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.html = render_template('emails/confirmacion.html', nombre=nombre)
        mail.send(msg)
        print(f"Correo enviado a {email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: Autenticación fallida. Verifica el usuario y contraseña de SMTP.")
    except smtplib.SMTPConnectError:
        print("Error: No se pudo conectar al servidor SMTP. Verifica MAIL_SERVER y MAIL_PORT.")
    except smtplib.SMTPException as e:
        print(f"Error SMTP: {e}")
    except Exception as e:
        print(f"Error general al enviar el correo: {e}")
    return False

def enviar_correo_cambio_password(email, nombre, temp_password):
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("Error: No se ha configurado el correo o la contraseña SMTP.")
        return False
    
    try:
        msg = Message(
            subject='Restablecimiento de Contraseña - UCE',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.html = render_template(
            'emails/cambio_password.html',
            nombre=nombre,
            temp_password=temp_password
        )
        mail.send(msg)
        print(f"Correo de cambio de contraseña enviado a {email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: Autenticación fallida. Verifica el usuario y contraseña de SMTP.")
    except smtplib.SMTPConnectError:
        print("Error: No se pudo conectar al servidor SMTP. Verifica MAIL_SERVER y MAIL_PORT.")
    except smtplib.SMTPException as e:
        print(f"Error SMTP: {e}")
    except Exception as e:
        print(f"Error general al enviar el correo: {e}")
    return False

def verificar_conexion_smtp():
    """Verifica la conexión SMTP al iniciar la aplicación."""
    try:
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        print("Conexión SMTP exitosa")
        server.quit()
    except smtplib.SMTPAuthenticationError:
        print("Error: Autenticación fallida. Verifica MAIL_USERNAME y MAIL_PASSWORD.")
    except smtplib.SMTPConnectError:
        print("Error: No se pudo conectar al servidor SMTP.")
    except Exception as e:
        print(f"Error de conexión SMTP: {e}")