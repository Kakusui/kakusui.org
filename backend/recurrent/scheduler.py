## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import json
import time
from datetime import datetime, timedelta

## third-party imports
import shelve

import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from sqlalchemy.orm import sessionmaker

## custom imports
from email_util.backup import perform_backup_scheduled

from constants import BACKUP_LOGS_DIR, VERIFICATION_DATA_DIR, RATE_LIMIT_DATA_DIR, DATABASE_PATH

def start_scheduler(SessionLocal:sessionmaker) -> None:

    """

    Starts the scheduler for the application.

    Args:
    BACKUP_LOGS_DIR (str): The directory to store the backup logs
    VERIFICATION_DATA_DIR (str): The directory to store the verification data
    RATE_LIMIT_DATA_DIR (str): The directory to store the rate limit data
    """

    max_retries = 5
    retry_delay = 3

    for _ in range(max_retries):
        try:
            with shelve.open(os.path.join(BACKUP_LOGS_DIR, 'backup_scheduler.db')) as db:
                last_run = db.get('last_run', None)

                should_run_initial = True
                if(last_run):
                    time_since_last_run = datetime.now() - last_run
                    if(time_since_last_run < timedelta(hours=6)):
                        should_run_initial = False

            break

        except Exception as e:
            if("Resource temporarily unavailable" in str(e)):
                time.sleep(retry_delay)
            else:
                raise
    else:
        print("Failed to initialize scheduler after multiple attempts")
        return

    if(should_run_initial):
        cleanup_expired_codes()
        perform_backup_scheduled(SessionLocal)

    scheduler = BackgroundScheduler()

    scheduler.add_job(lambda: perform_backup_scheduled(SessionLocal), 'interval', hours=6)
    scheduler.add_job(cleanup_expired_codes, 'interval', hours=1)

    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())

def cleanup_expired_codes() -> None:

    """

    Cleans up the expired codes in the verification data directory and the rate limit data directory.

    Args:
    VERIFICATION_DATA_DIR (str): The directory to store the verification data
    RATE_LIMIT_DATA_DIR (str): The directory to store the rate limit data
    """

    if(not os.path.exists(VERIFICATION_DATA_DIR)):
        return

    current_time = datetime.now()

    for filename in os.listdir(VERIFICATION_DATA_DIR):
        file_path = os.path.join(VERIFICATION_DATA_DIR, filename)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            expiration_time = datetime.fromisoformat(data['expiration'])

            if(current_time > expiration_time):
                os.remove(file_path)
                print(f"Removed expired verification code for {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    if(not os.path.exists(RATE_LIMIT_DATA_DIR)):
        return

    for filename in os.listdir(RATE_LIMIT_DATA_DIR):
        file_path = os.path.join(RATE_LIMIT_DATA_DIR, filename)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            blocked_until = data.get('blocked_until')

            if(blocked_until and current_time.timestamp() > blocked_until):
                os.remove(file_path)
                print(f"Removed expired rate limit file for {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")