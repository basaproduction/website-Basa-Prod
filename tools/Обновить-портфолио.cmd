@echo off
where py >nul 2>nul
if errorlevel 1 goto python
py -3 "%~dp0update_portfolio.py"
goto done
:python
python "%~dp0update_portfolio.py"
:done
pause
