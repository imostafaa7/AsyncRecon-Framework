#!/bin/bash
set -e

echo "[*] إعداد بيئة التشغيل..."
VENV_DIR="recon_env"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

chmod +x async_recon.py
sudo cp async_recon.py /usr/local/bin/async_recon
echo "[+] التثبيت اكتمل. يمكنك التشغيل عبر: $VENV_DIR/bin/python async_recon.py أو الأداة العامة async_recon (يتطلب نقل البيئة)."
