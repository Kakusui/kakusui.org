## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import json
import asyncio
from datetime import datetime, timedelta
import logging
from pathlib import Path

## third-party imports
import shelve
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

## custom modules
from auth.util import is_safe_filename

## custom imports
from email_util.backup import perform_backup_scheduled
from constants import BACKUP_LOGS_DIR, VERIFICATION_DATA_DIR, RATE_LIMIT_DATA_DIR

async def start_scheduler(db:Session) -> AsyncIOScheduler:
    """
    Starts the scheduler for the application.

    Args:
    db (Session): The database session
    """
    max_retries = 5
    retry_delay = 3

    for _ in range(max_retries):
        try:
            with shelve.open(os.path.join(BACKUP_LOGS_DIR, 'backup_scheduler.db')) as database:
                last_run = database.get('last_run', None)

                should_run_initial = True
                if(last_run):
                    time_since_last_run = datetime.now() - last_run
                    if(time_since_last_run < timedelta(hours=6)):
                        should_run_initial = False

            break
        except Exception as e:
            if("Resource temporarily unavailable" in str(e)):
                await asyncio.sleep(retry_delay)
            else:
                raise
    else:
        raise Exception("Failed to initialize scheduler after multiple attempts")

    if(should_run_initial):
        await cleanup_expired_codes()
        await perform_backup_scheduled(db)

    scheduler = AsyncIOScheduler()

    scheduler.add_job(perform_backup_scheduled, 'interval', hours=6, args=[db])
    scheduler.add_job(cleanup_expired_codes, 'interval', hours=1)

    scheduler.start()

    return scheduler

async def cleanup_expired_codes() -> None:
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
        if not await is_safe_filename(filename):
            logging.warning(f"Skipping potentially unsafe filename: {filename}")
            continue

        file_path = Path(VERIFICATION_DATA_DIR) / filename

        try:
            with file_path.open('r') as f:
                data = json.load(f)
            expiration_time = datetime.fromisoformat(data['expiration'])

            if(current_time > expiration_time):
                file_path.unlink()
                logging.info(f"Removed expired verification code file")

        except Exception as e:
            logging.error(f"Error processing verification file: {str(e)}")

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
                logging.info(f"Removed expired rate limit file for {filename}")

        except Exception as e:
            logging.error(f"Error processing {filename}: {str(e)}")