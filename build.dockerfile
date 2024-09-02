## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

FROM python:3.11.8-slim

WORKDIR /app

## Copy backend files
COPY backend/main.py backend/requirements.txt ./backend/

## Install required Python packages
RUN pip install --no-cache-dir -r backend/requirements.txt && \
    python -m spacy download ja_core_news_lg

## Install required packages (linux) including GPG
RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

## Copy entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

## Expose port 8000
EXPOSE 8000

## Start the app
CMD ["./entrypoint.sh"]