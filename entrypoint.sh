#!/bin/sh

## Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2 --limit-max-requests 25