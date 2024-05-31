## Stage 1: Build frontend
FROM node:20.13.1 as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

## Stage 2: Build backend
FROM python:3.11.8-slim as backend-build
WORKDIR /app/backend
COPY backend/ ./

## Install Python dependencies, set up the environment files for both frontend and backend
RUN python setup.py install

## Stage 3: Final stage
FROM python:3.11.8-slim
WORKDIR /app

## Install nginx and other required packages
RUN apt-get update && apt-get install -y nginx && apt-get clean

## Copy backend from the previous stage
COPY --from=backend-build /app/backend /app/backend

## Copy frontend build from the previous stage
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

## Copy requirements file from backend to the current stage
COPY backend/requirements.txt /app/backend/requirements.txt

## Install required Python packages
RUN pip install -r /app/backend/requirements.txt
RUN python3 -c "\
import spacy;\
nlp = spacy.load('ja_core_news_lg', disable=['parser', 'ner']);\
" || python3 -m spacy download ja_core_news_lg

## Copy nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

## Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

## Expose port 80
EXPOSE 80

## Start the app
CMD ["/app/entrypoint.sh"]