@ECHO OFF
apache\configure.py %*
IF ERRORLEVEL 1 GOTO error
start apache\bin\httpd.exe
exit

:error
pause