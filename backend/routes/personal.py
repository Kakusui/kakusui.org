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
    random_number = random.randint(1, 4)
    
    sites_list = [
        'https://sliding.toys/mystic-square/8-puzzle/daily/',
        'https://longdogechallenge.com/',
        'https://maze.toys/mazes/mini/daily/',
        'https://optical.toys',
        'https://paint.toys/',
        'https://puginarug.com',
        'https://memory.toys/classic/easy/',
        'https://alwaysjudgeabookbyitscover.com',
        'https://clicking.toys/flip-grid/neat-nine/3-holes/',
        'https://weirdorconfusing.com/',
        'https://checkbox.toys/scale/',
        'https://binarypiano.com/',
        'https://mondrianandme.com/',
        'https://onesquareminesweeper.com/',
        'https://cursoreffects.com',
        'http://floatingqrcode.com/',
        'https://thatsthefinger.com/',
        'https://cant-not-tweet-this.com/',
        'http://heeeeeeeey.com/',
        'http://corndog.io/',
        'http://eelslap.com/',
        'http://www.staggeringbeauty.com/',
        'http://burymewithmymoney.com/',
        'https://smashthewalls.com/',
        'https://jacksonpollock.org/',
        'http://endless.horse/',
        'http://drawing.garden/',
        'https://www.trypap.com/',
        'http://www.republiquedesmangues.fr/',
        'http://www.movenowthinklater.com/',
        'https://sliding.toys/klotski/easy-street/',
        'https://paint.toys/calligram/',
        'https://checkboxrace.com/',
        'http://www.rrrgggbbb.com/',
        'http://www.koalastothemax.com/',
        'https://rotatingsandwiches.com/',
        'http://www.everydayim.com/',
        'http://randomcolour.com/',
        'http://maninthedark.com/',
        'http://cat-bounce.com/',
        'http://chrismckenzie.com/',
        'https://thezen.zone/',
        'http://ninjaflex.com/',
        'http://ihasabucket.com/',
        'http://corndogoncorndog.com/',
        'http://www.hackertyper.com/',
        'https://pointerpointer.com',
        'http://imaninja.com/',
        'http://www.partridgegetslucky.com/',
        'http://www.ismycomputeron.com/',
        'http://www.nullingthevoid.com/',
        'http://www.muchbetterthanthis.com/',
        'http://www.yesnoif.com/',
        'http://lacquerlacquer.com',
        'http://potatoortomato.com/',
        'http://iamawesome.com/',
        'https://strobe.cool/',
        'http://thisisnotajumpscare.com/',
        'http://doughnutkitten.com/',
        'http://crouton.net/',
        'http://corgiorgy.com/',
        'http://www.wutdafuk.com/',
        'http://unicodesnowmanforyou.com/',
        'http://chillestmonkey.com/',
        'http://scroll-o-meter.club/',
        'http://www.crossdivisions.com/',
        'http://tencents.info/',
        'https://memory.toys/maze/easy/',
        'https://boringboringboring.com/',
        'http://www.patience-is-a-virtue.org/',
        'http://pixelsfighting.com/',
        'http://isitwhite.com/',
        'https://existentialcrisis.com/',
        'http://onemillionlols.com/',
        'http://www.omfgdogs.com/',
        'http://oct82.com/',
        'http://chihuahuaspin.com/',
        'http://www.blankwindows.com/',
        'http://tunnelsnakes.com/',
        'http://www.trashloop.com/',
        'http://spaceis.cool/',
        'https://elonjump.com/',
        'http://www.doublepressure.com/',
        'http://www.donothingfor2minutes.com/',
        'http://buildshruggie.com/',
        'http://yeahlemons.com/',
        'http://wowenwilsonquiz.com',
        'http://notdayoftheweek.com/',
        'http://www.amialright.com/',
        'https://optical.toys/thatcher-effect/',
        'https://greatbignothing.com/',
        'https://zoomquilt.org/',
        'https://dadlaughbutton.com/',
        'https://remoji.com/',
        'http://papertoilet.com/',
        'https://loopedforinfinity.com/',
        'https://www.ripefordebate.com/',
        'https://end.city/',
        'https://www.bouncingdvdlogo.com/',
        'https://clicking.toys/peg-solitaire/english/',
        'https://toms.toys'
    ]
    
    url_map = {
        1: "https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1",  ## Rick Roll
        2: "https://www.youtube.com/watch?v=ZZ5LpwO-An4&autoplay=1",  ## He-Man HEYYEYAAEYAAAEYAEYAA
        3: "https://neal.fun/absurd-trolley-problems/",  ## Absurd Trolley Problems
        4: random.choice(sites_list)  ## Random fun website
    }

    return RedirectResponse(url=url_map[random_number])