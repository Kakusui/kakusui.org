## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## Stage 1: Build backend
FROM python:3.11.8-slim as backend-build
WORKDIR /app/backend
COPY backend/main.py backend/requirements.txt ./

## Install required Python packages
FROM python:3.11.8-slim
WORKDIR /app

## Install required packages (linux)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

## Copy backend from the previous stage
COPY --from=backend-build /app/backend/main.py /app/backend/main.py
COPY --from=backend-build /app/backend/requirements.txt /app/backend/requirements.txt

## Install required Python packages
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && python3 -c "\
import spacy;\
nlp = spacy.load('ja_core_news_lg', disable=['parser', 'ner']);\
" || python3 -m spacy download ja_core_news_lg

## Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

## Expose port 8000
EXPOSE 8000

## Start the app
CMD ["/app/entrypoint.sh"]