## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import asyncio
import typing
import smtplib
import aiofiles

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

##----------------------------------/----------------------------------##

async def get_smtp_envs() -> typing.Tuple[str, str, int, str, str, str, str]:

    """
    
    Get the environment variables from the .env file

    Returns:
    ENCRYPTION_KEY (str): The encryption key to encrypt/decrypt the database
    SMTP_SERVER (str): The SMTP server to send the email
    SMTP_PORT (int): The SMTP port to send the email
    SMTP_USER (str): The SMTP user to send the email
    SMTP_PASSWORD (str): The SMTP password to send the email
    FROM_EMAIL (str): The email address to send the email from
    TO_EMAIL (str): The email address to send the email to

    """

    if(await asyncio.to_thread(os.path.exists, ".env")):
        async with asyncio.Lock():
            async with aiofiles.open(".env", "r") as f:
                lines = await f.readlines()
                for line in lines:
                    key, value = line.strip().split("=")
                    os.environ[key] = value

    ENCRYPTION_KEY:str = os.getenv('ENCRYPTION_KEY') or ""
    SMTP_SERVER:str = os.getenv('SMTP_SERVER') or ""
    SMTP_PORT:int = int(os.getenv('SMTP_PORT') or 0)
    SMTP_USER = os.getenv('SMTP_USER') or ""
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD') or ""
    FROM_EMAIL = os.getenv('FROM_EMAIL') or ""
    TO_EMAIL = os.getenv('TO_EMAIL') or ""

    assert(ENCRYPTION_KEY != ""), "ENCRYPTION_KEY is required"
    assert(SMTP_SERVER != ""), "SMTP_SERVER is required"
    assert(SMTP_PORT != 0), "SMTP_PORT is required"
    assert(SMTP_USER != ""), "SMTP_USER is required"
    assert(SMTP_PASSWORD != ""), "SMTP_PASSWORD is required"
    assert(FROM_EMAIL != ""), "FROM_EMAIL is required"
    assert(TO_EMAIL != ""), "TO_EMAIL is required"

    return ENCRYPTION_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL

##----------------------------------/----------------------------------##

async def send_email(subject:str, body:str, to_email:str, attachment_path:str | None, from_email:str, smtp_server:str, smtp_port:int, smtp_user:str, smtp_password:str) -> None:

    """

    Send an email with an attachment

    Args:
    subject (str): The subject of the email
    body (str): The body of the email
    to_email (str): The email address to send the email to
    attachment_path (str): The path to the attachment to send
    from_email (str): The email address to send the email from
    smtp_server (str): The SMTP server to send the email
    smtp_port (int): The SMTP port to send the email
    smtp_user (str): The SMTP user to send the email
    smtp_password (str): The SMTP password to send the email

    """

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    msg.attach(MIMEText(body, 'plain'))

    if(attachment_path is not None):
        async with aiofiles.open(attachment_path, 'rb') as f:
            content = await f.read()
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            msg.attach(part)

    try:
        await asyncio.to_thread(send_email_sync, msg, smtp_server, smtp_port, smtp_user, smtp_password)
        
    except Exception as e:
        print(f"Error: {e}")

def send_email_sync(msg, smtp_server, smtp_port, smtp_user, smtp_password):
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls() 
        server.login(smtp_user, smtp_password)
        server.send_message(msg)