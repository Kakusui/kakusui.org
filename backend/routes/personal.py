## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import random

router = APIRouter()

@router.get("/kbilyeu/something_entertaining")
async def something_entertaining():
    random_number = random.randint(1, 5)
    
    url_map = {
        1: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  ## Rick Roll
        2: "https://www.youtube.com/watch?v=Z1BCujX3pw8",  ## He-Man HEYYEYAAEYAAAEYAEYAA
        3: "https://neal.fun/absurd-trolley-problems/",  ## Absurd Trolley Problems
        4: "https://theuselessweb.com",  ## Random Useless Website
        5: "https://thispersondoesnotexist.com"  ## Existential Crisis Generator
    }

    return RedirectResponse(url=url_map[random_number])