source ./.venv/bin/activate
mpremote fs rm -rf :./
mpremote fs cp -r src/* :./
mpremote reset
mpremote