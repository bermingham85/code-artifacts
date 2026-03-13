@echo off
:: APEX PH-08 Watchdog launcher
:: Point Windows Task Scheduler at this file.
cd /d C:\Users\bermi\Projects\apex
python watchdog\watchdog.py >> logs\watchdog_sched.log 2>&1
