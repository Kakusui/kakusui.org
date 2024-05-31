## Frontend Dockerfile
FROM node:20-alpine

## Create app directory
WORKDIR /app

## Install app dependencies
COPY package*.json ./
RUN npm install

## Copy app source code
COPY . .

## Build the app
RUN npm run build

## Install serve to serve the frontend
RUN npm install -g serve

## Expose the port
EXPOSE 3000

## Start the app
CMD ["serve", "-s", "dist", "-l", "3000"]
