## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

import os 

def get_env_variables() -> None:

    """

    Only used in development. This function reads the .env file and sets the environment variables.

    """

    if(not os.path.exists(".env")):
        return

    with open(".env") as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key] = value

get_env_variables()

TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS_HASH = os.environ.get("ADMIN_PASS_HASH")
TOTP_SECRET = os.environ.get("TOTP_SECRET")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = os.environ.get("REFRESH_TOKEN_SECRET")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

TOKEN_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 43200 ## 30 days
VERIFICATION_EXPIRATION_MINUTES = 5
MAX_REQUESTS = 5
MAX_REQUESTS_PER_ID = 10
MAX_REQUESTS_PER_EMAIL = 5
RATE_LIMIT_WINDOW = 3600

V1_KAIRYOU_ROOT_KEY = os.environ.get("V1_KAIRYOU_ROOT_KEY")
V1_EASYTL_ROOT_KEY = os.environ.get("V1_EASYTL_ROOT_KEY")
V1_EASYTL_PUBLIC_API_KEY = os.environ.get("V1_EASYTL_PUBLIC_API_KEY")
V1_ELUCIDATE_ROOT_KEY = os.environ.get("V1_ELUCIDATE_ROOT_KEY")

DATABASE_URL: str = "sqlite:///./database/kakusui.db"
DATABASE_PATH: str = "database/kakusui.db"
BACKUP_LOGS_DIR = 'database/logs'
VERIFICATION_DATA_DIR = 'database/temp_verification'
RATE_LIMIT_DATA_DIR = 'database/rate_limit'

__all__ = ["TURNSTILE_SECRET_KEY", 
           "ENCRYPTION_KEY", 
           "ADMIN_USER", 
           "ADMIN_PASS_HASH", 
           "TOTP_SECRET", 
           "ACCESS_TOKEN_SECRET", 
           "REFRESH_TOKEN_SECRET", 
           "TURNSTILE_SECRET_KEY", 
           "ENVIRONMENT", 
           "TOKEN_ALGORITHM", 
           "TOKEN_EXPIRE_MINUTES", 
           "VERIFICATION_EXPIRATION_MINUTES", 
           "MAX_REQUESTS", 
           "MAX_REQUESTS_PER_ID", 
           "MAX_REQUESTS_PER_EMAIL", 
           "RATE_LIMIT_WINDOW", 
           "V1_KAIRYOU_ROOT_KEY", 
           "V1_EASYTL_ROOT_KEY", 
           "V1_EASYTL_PUBLIC_API_KEY", 
           "V1_ELUCIDATE_ROOT_KEY", 
           "DATABASE_URL", 
           "DATABASE_PATH", 
           "BACKUP_LOGS_DIR", 
           "VERIFICATION_DATA_DIR", 
           "RATE_LIMIT_DATA_DIR"]