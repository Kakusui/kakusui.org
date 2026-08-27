## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

import asyncio
from weakref import WeakKeyDictionary


VALID_LLM_SERVICES = {"anthropic", "gemini", "openai"}
_provider_locks: WeakKeyDictionary[
    asyncio.AbstractEventLoop,
    dict[str, asyncio.Lock],
] = WeakKeyDictionary()


def get_llm_provider_lock(service: str) -> asyncio.Lock:
    if(service not in VALID_LLM_SERVICES):
        raise ValueError(f"Unsupported LLM service: {service}")

    event_loop = asyncio.get_running_loop()
    loop_locks = _provider_locks.setdefault(event_loop, {})
    return loop_locks.setdefault(service, asyncio.Lock())
