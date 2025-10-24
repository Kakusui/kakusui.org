## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
from datetime import datetime, timedelta

## third-party imports
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from filelock import FileLock, Timeout

## custom imports
from email_util.backup import perform_backup_scheduled
from auth.func import cleanup_expired_verification_data
from rate_limit.func import cleanup_old_rate_limit_data
from util import KairyouCache

import logging

## In-memory storage
last_backup_run = None
LOCK_FILE = "scheduler_lock.lock"

lock = FileLock(LOCK_FILE, timeout=1)  # 1 second timeout

async def start_scheduler(db:Session) -> AsyncIOScheduler:
    """
    Starts the scheduler for the application.

    Args:
    db (Session): The database session
    """
    global last_backup_run

    should_run_initial = True
    if(last_backup_run):
        time_since_last_run = datetime.now() - last_backup_run
        if(time_since_last_run < timedelta(hours=6)):
            should_run_initial = False

    if(should_run_initial):
        try:
            with lock:
                await cleanup_expired_verification_data()
                await cleanup_old_rate_limit_data()

                # Check if backup emails are enabled before running backup
                try:
                    from email_util.common import get_smtp_envs
                    _, _, _, _, _, _, _, enable_emails = await get_smtp_envs()
                    if enable_emails:
                        await perform_backup_scheduled(db)
                        last_backup_run = datetime.now()
                    else:
                        logging.info("Backup emails disabled by ENABLE_BACKUP_EMAILS environment variable. Skipping initial backup.")
                except Exception as e:
                    logging.error(f"Error checking backup email settings: {e}")

        except Timeout:
            print("Another instance is already running the initial tasks.")

    scheduler = AsyncIOScheduler()

    scheduler.add_job(perform_backup_and_update_time, 'interval', hours=6, args=[db])
    scheduler.add_job(cleanup_expired_verification_data, 'interval', minutes=5)
    scheduler.add_job(cleanup_old_rate_limit_data, 'interval', minutes=5)
    scheduler.add_job(cleanup_kairyou_model_cache, 'interval', minutes=1)  # Check every minute for model timeout

    scheduler.start()

    return scheduler

async def cleanup_kairyou_model_cache() -> None:
    """
    Cleanup Kairyou model cache if timeout has been reached.
    This helps free up memory when the model hasn't been used for a while.
    """
    if(KairyouCache.should_unload_model()):
        logging.info(f"Kairyou model timeout reached – unloading model. Cache status: {KairyouCache.get_status()}")
        try:
            from kairyou import Kairyou as _K
            if(hasattr(_K, "_ner")):
                _K._ner = None
                logging.info("SpaCy model reference cleared by scheduler")
        except Exception as e:
            logging.error(f"Error while clearing SpaCy model in scheduler: {e}")

        KairyouCache.mark_model_unloaded()
        logging.info("Kairyou model marked as unloaded to save memory")

async def perform_backup_and_update_time(db:Session) -> None:
    """
    Performs the backup and updates the last run time.

    Args:
    db (Session): The database session
    """
    global last_backup_run
    try:
        with lock:
            # Check if backup emails are enabled before running backup
            try:
                from email_util.common import get_smtp_envs
                _, _, _, _, _, _, _, enable_emails = await get_smtp_envs()
                if enable_emails:
                    await perform_backup_scheduled(db)
                    last_backup_run = datetime.now()
                else:
                    logging.info("Backup emails disabled by ENABLE_BACKUP_EMAILS environment variable. Skipping scheduled backup.")
            except Exception as e:
                logging.error(f"Error checking backup email settings during scheduled backup: {e}")
    except Timeout:
        print("Another instance is already performing the backup.")
