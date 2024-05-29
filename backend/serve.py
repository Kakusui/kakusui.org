## Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

from waitress import serve
from app import app  

## for production
if(__name__ == "__main__"):
    serve(app, host='0.0.0.0', port=5000)
