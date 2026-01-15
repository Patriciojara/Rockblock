@echo off
REM Ejecuta send_lora_clean.py en Windows usando COM7 y espera ACK
cd /d "%~dp0"
python send_lora_clean.py --port COM7 --wait-ack open
pause
