---------------------------------------------------------------------------------------------------------------------------------------------------
**Table of Contents**

- [**Preface**](#preface)
- [**Prerequisites**](#prerequisites)
- [**Python Requirements**](#python-requirements)
- [**Node Requirements**](#node-requirements)
- [**To build locally (Manual)**](#to-build-locally-manual)
  - [**Raw Docker Method**](#raw-docker-method)
    - [**Backend**](#backend)
    - [**Frontend**](#frontend)
  - [**Docker Compose Method**](#docker-compose-method)
- [**For Production**](#for-production)
  - [**Frontend**](#frontend-1)
  - [**Backend**](#backend-1)
    - [To deploy to fly.io](#to-deploy-to-flyio)
- [**Contributing**](#contributing)
- [**License**](#license)

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Preface**<a name="preface"></a>
This is the repository for the website of Kakusui LLC (kakusui.org). All code is open-source and available for anyone to use. Below is a brief overview of the project, how to build it locally, information regarding production, licensing, and contributing.

If you need to report a security vulnerability, please see the [SECURITY.md](SECURITY.md) file.

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Prerequisites**<a name="prerequisites"></a>
python (runs on 3.11.8, lowest tested version is 3.11.4)

node 20.13.1

npm 10.8.0

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Python Requirements**<a name="python-requirements"></a>
ja-core-news-lg==3.7.0 (this is not a pip package, it is a spacy model) Must be installed via spacy. (Done in setup.py)

fastapi==0.110.3

kairyou==1.6.5

uvicorn==0.30.0

easytl==0.4.9

aiofiles==23.2.1

httpx==0.25.1

elucidate==0.0.2

passlib==1.7.4

pyotp==2.9.0

bcrypt==3.1.7

sqlalchemy==2.0.31

python-gnupg==0.5.2

apscheduler==3.10.4

pyjwt==2.8.0

python-multipart==0.0.9

werkzeug==3.0.4

stripe==10.12.0

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Node Requirements**<a name="node-requirements"></a>
See `frontend/package.json` for a list of node requirements.

--------------------------------------------------------------------------------------------------------------------------------------------------

## **To build locally (Manual)**<a name="build-locally"></a>

> [!TIP] 
> This may not work on linux, if you are using linux, we reccomend using the docker method below.
 
1. Clone the repo, make sure you are using the correct branch (currently `production`)
2. Navigate to the `backend` directory. `cd backend`. Inside is the python backend.
3. Run the setup script with the local argument. This will install all requirements and setup the local env `python setup.py local`.
4. Run the server. For local `uvicorn main:app --reload --port 5000`
5. Open a new terminal and navigate to the `frontend` directory. `cd frontend`. Inside is the react (vite) frontend.
6. First install all required packages, these are in `package.json`. Do `npm i`. Then run the dev server with `npm run dev`
7. Website will be on localhost:5173 (frontend) and localhost:5000 (backend)


### **Raw Docker Method**<a name="docker-method"></a>
1. Clone the repo, make sure you are using the correct branch (currently `production`)

#### **Backend**<a name="backend"></a>

1. `cd backend`
2. `docker build -t kakusui-org-backend -f Dockerfile.dev .`
3. `docker run -p 5000:5000 kakusui-org-backend`

#### **Frontend**<a name="frontend"></a>

1. `cd frontend`
2. `docker build -t kakusui-org-frontend -f Dockerfile .`
3. `docker run -p 5173:5173 kakusui-org-frontend`

### **Docker Compose Method**<a name="docker-compose-method"></a>

> [!TIP]
> We are using docker compose v2 so `docker compose up --build` is the command we use, adjust as needed if you are using an older version of docker compose.

Run `docker compose up --build` from the root directory.


## **For Production**<a name="for-production"></a>

### **Frontend**<a name="frontend-1"></a>

Frontend is hosted on cloudflare pages. To deploy, push to the `production` branch. Development branch is for development only, intermediate builds deploy every commit.

### **Backend**<a name="backend-1"></a>

For production, the backend is hosted on fly.io via a dockerfile.

#### To deploy to fly.io
1. Make sure you have the fly cli installed and are logged in.
2. Run `fly deploy` in the backend directory `cd backend`. This will build the dockerfile and deploy it to fly.io.

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Contributing**<a name="contributing"></a>
If you would like to contribute, please open an issue or a pull request. No specific guidelines, but remain professional.

--------------------------------------------------------------------------------------------------------------------------------------------------

## **License**<a name="license"></a>

As Kakusui is an avid supporter of open-source software, this project is licensed under one of the strongest copyleft licenses available, the GNU Affero General Public License (AGPLv3).

You can find the full text of the license in the [LICENSE](License.md) file.

The AGPLv3 is a copyleft license that promotes the principles of open-source software. It ensures that any derivative works based on this project, as well as any software that interacts with users over a network, must also be distributed under the same AGPLv3 license. This license grants you the freedom to use, modify, and distribute the software.

Please note that this information is a brief summary of the AGPLv3. For a detailed understanding of your rights and obligations under this license, please refer to the full license text.