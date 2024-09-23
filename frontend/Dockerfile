## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

FROM node:20.13.1

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .


EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]