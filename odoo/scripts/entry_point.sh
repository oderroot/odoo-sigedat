#!/bin/bash
set -e

COMMAND=${ODOO_COMMAND}
MODULE=${MODULE:-base}

# Función para iniciar LibreOffice en modo headless
start_libreoffice() {
  if ! pgrep -f "libreoffice.*socket,host=localhost,port=8100" > /dev/null; then
    echo ">> Iniciando LibreOffice en modo headless..."
    # /usr/bin/libreoffice --headless --accept="socket,host=localhost,port=8100,tcpNoDelay=1;urp;" &
    /usr/bin/soffice --headless --norestore --nologo --nofirststartwizard --accept="socket,port=2002;urp;" &
    sleep 5
    echo ">> LibreOffice iniciado."
  else
    echo ">> LibreOffice ya está en ejecución."
  fi
}

# Inicia el servidor HTTP
python3 -m http.server 8080 --directory /mnt/extra-addons/sigedat/static/src &

start_libreoffice


echo ">> ODOO_COMMAND: $COMMAND"
echo ">> MODULE: $MODULE"

case "$COMMAND" in
  run)
    echo ">> Starting Odoo normally..."
    exec odoo -c /etc/odoo/odoo.conf
    ;;
  debug)
    echo ">> Starting Odoo in debug mode on port 8888..."
    exec python3 -m debugpy --listen 0.0.0.0:8888 /usr/bin/odoo -c /etc/odoo/odoo.conf --log-handler odoo.tools.convert:DEBUG
    ;;
  install_or_update)
    echo ">> Installing/updating module: $MODULE"
    exec odoo -c /opt/odoo/odoo.conf -u $MODULE --stop-after-init
    ;;
  *)
    echo ">> Unknown command: $COMMAND"
    exit 1
    ;;
esac
