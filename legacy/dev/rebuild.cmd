@ECHO OFF
REM
REM If we have a zip from MR, unzip it and rename
REM appropriately. Always overwrite a local file of the same
REM name.
REM
ECHO Looking for new .zip file
IF EXIST "data\Masses Access 2007.zip" (
    unzip -o "data\Masses Access 2007.zip" -d data
    move /y "data\Masses Access 2007.accdb" "data\masses.accdb"
    move /y "data\Masses Access 2007.zip" "data\Masses Access 2007.used.zip"
)
IF EXIST "data\Masses Access 2002.zip" (
    unzip -o "data\Masses Access 2002.zip" -d data
    move /y "data\Masses Access 2002.mdb" "data\masses.mdb"
    move /y "data\Masses Access 2002.zip" "data\Masses Access 2002.used.zip"
)

REM
REM If we have an .mdb or .accdb of the right name (possibly as a result
REM of the last step) bzip it up. Now unbzip the packed masses.accdb or mdb
REM and remove any existing masses.db so we have a clean start.
REM
ECHO Bzipping masses.accdb or mdb and clearing masses.db
IF EXIST "data\masses.accdb" bzip2 -f data\masses.accdb
IF EXIST "data\masses.accdb.bz2" bunzip2 -v -f data\masses.accdb.bz2
IF ERRORLEVEL 1 (
    ECHO !! Problem
    GOTO finish
)
IF EXIST "data\masses.mdb" bzip2 -f data\masses.mdb
IF EXIST "data\masses.mdb.bz2" bunzip2 -v -f data\masses.mdb.bz2
IF ERRORLEVEL 1 (
    ECHO !! Problem
    GOTO finish
)
ECHO %ERRORLEVEL%
DEL data\masses.db

REM
REM If we have an .accdb *and* an .mdb something's gone
REM wrong; we should have only one or the other!
REM
IF EXIST "data\masses.mdb" (
    IF EXIST "data\masses.accdb" (
        ECHO !! We have both an .mdb and an .accdb
        GOTO finish
    )
)

REM
REM Build an empty database by piping the DDL into
REM sqlite3 and then run the Python build script.
REM
ECHO Creating empty database
sqlite3 data\masses.db < create.sql
IF ERRORLEVEL 1 (
    ECHO !! Problem
    GOTO finish
)

ECHO Building Data
py -2 mdb2sqlite.py
IF ERRORLEVEL 1 (
    ECHO !! Problem
    GOTO finish
)

REM
REM Finally bzip up again ready for deployment
REM
ECHO BZipping .accdb
IF EXIST "data\masses.accdb" bzip2 -v data\masses.accdb
IF ERRORLEVEL 1 (
    ECHO !! Problem
    GOTO finish
)
ECHO BZipping .mdb
IF EXIST "data\masses.mdb" bzip2 -v data\masses.mdb
IF ERRORLEVEL 1 (
    ECHO !! Problem
    GOTO finish
)

del /Q cache\*
py -2 warm-cache.py > warm-cache.log
IF ERRORLEVEL 1 (
    ECHO !! Problem
    GOTO finish
)

:finish
pause