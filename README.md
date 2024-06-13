---------------------------------------------------------------------------------------------------------------------------------------------------
**Table of Contents**

- [**Preface**](#preface)
- [**Prerequisites**](#prerequisites)
- [**Python Requirements**](#python-requirements)
- [**Node Requirements**](#node-requirements)
- [**To build locally**](#to-build-locally)
- [**For Production**](#for-production)
  - [To test the dockerfile locally](#to-test-the-dockerfile-locally)
  - [To deploy to fly.io](#to-deploy-to-flyio)
- [**Contributing**](#contributing)
- [**License**](#license)

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Preface**<a name="preface"></a>
This is the repository for the website of Kakusui LLC (kakusui.org). All code is open-source and available for anyone to use. Below is a brief overview of the project, how to build it locally, information regarding production, licensing, and contributing. 

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Prerequisites**<a name="prerequisites"></a>
python (runs on 3.11.8, lowest tested version is 3.11.4)

node 20.13.1

npm 10.8.0

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Python Requirements**<a name="python-requirements"></a>
fastapi==0.110.3

kairyou==1.6.4

uvicorn==0.30.0

ja-core-news-lg==3.7.0 (this is not a pip package, it is a spacy model) Must be installed via spacy. (Done in setup.py)

httpx==0.25.1

easytl==0.4.3

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Node Requirements**<a name="node-requirements"></a>
See `frontend/package.json` for a list of node requirements.

--------------------------------------------------------------------------------------------------------------------------------------------------

## **To build locally**<a name="build-locally"></a>
1. Clone the repo, make sure you are using the correct branch (currently `production`)
2. Navigate to the `backend` directory. `cd backend`. Inside is the python backend.
3. Run the setup script with the local argument. This will install all requirements and setup the local env `python setup.py local`.
4. Run the server. For local `uvicorn main:app --reload --port 5000 --workers 2 --limit-max-requests 25`
5. Open a new terminal and navigate to the `frontend` directory. `cd frontend`. Inside is the react (vite) frontend.
6. First install all required packages, these are in `package.json`. Do `npm i`. Then run the dev server with `npm run dev`
7. Website will be on localhost:5173 (frontend) and localhost:5000 (backend)

--------------------------------------------------------------------------------------------------------------------------------------------------

## **For Production**<a name="for-production"></a>

For production, the backend is hosted on fly.io via a dockerfile.

### To test the dockerfile locally
1. docker build -t kakusui-org -f build.dockerfile .
2. docker run -p 8000:8000 kakusui-org

### To deploy to fly.io
1. Make sure you have the fly cli installed and are logged in.
2. Run `fly deploy` in the root directory. This will build the dockerfile and deploy it to fly.io.

Frontend is hosted on cloudflare pages. To deploy, push to the `production` branch. Development branch is for development only, intermediate builds deploy every commit.

--------------------------------------------------------------------------------------------------------------------------------------------------

## **Contributing**<a name="contributing"></a>
If you would like to contribute, please open an issue or a pull request. No specific guidelines yet, but please be respectful.

--------------------------------------------------------------------------------------------------------------------------------------------------

## **License**<a name="license"></a>

As Kakusui is an avid supporter of open-source software, this project is licensed under one of the strongest copyleft licenses available, the GNU General Public License (GPL).

You can find the full text of the license in the [LICENSE](License.md) file.

The GPL is a copyleft license that promotes the principles of open-source software. It ensures that any derivative works based on this project must also be distributed under the same GPL license. This license grants you the freedom to use, modify, and distribute the software.

Please note that this information is a brief summary of the GPL. For a detailed understanding of your rights and obligations under this license, please refer to the full license text.
