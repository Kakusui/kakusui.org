#!/bin/sh

## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

invalid_volume_path="$(find /app/database -mindepth 1 \( ! -user 10001 -o ! -group 10001 -o ! -writable \) -print -quit)"
if [ ! -w /app/database ] || [ -n "$invalid_volume_path" ]; then
    echo "database volume must be writable by UID/GID 10001" >&2
    exit 1
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
