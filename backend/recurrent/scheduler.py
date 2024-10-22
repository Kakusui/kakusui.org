## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
from datetime import datetime, timedelta

## third-party imports
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

## custom imports
from email_util.backup import perform_backup_scheduled
from auth.func import cleanup_expired_verification_data
from rate_limit.func import cleanup_old_rate_limit_data

## In-memory storage
last_backup_run = None

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
        await cleanup_expired_verification_data()
        await cleanup_old_rate_limit_data()
        await perform_backup_scheduled(db)
        last_backup_run = datetime.now()

    scheduler = AsyncIOScheduler()

    scheduler.add_job(perform_backup_and_update_time, 'interval', hours=6, args=[db])
    scheduler.add_job(cleanup_expired_verification_data, 'interval', minutes=5)
    scheduler.add_job(cleanup_old_rate_limit_data, 'interval', minutes=5)

    scheduler.start()

    return scheduler

async def perform_backup_and_update_time(db:Session) -> None:
    """
    Performs the backup and updates the last run time.

    Args:
    db (Session): The database session
    """
    global last_backup_run
    await perform_backup_scheduled(db)
    last_backup_run = datetime.now()
