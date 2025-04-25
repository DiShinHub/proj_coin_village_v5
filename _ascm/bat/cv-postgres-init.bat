@echo off

cd ../../docker-compose/env

REM .env 파일 경로
set ENV_FILE=.\.env

REM .env 로드
for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if not "%%A"=="" set %%A=%%B
)

cd ../../_ascm/sql

REM DB 접속 정보
set PGHOST=localhost
set PGPORT=%POSTGRES_CONTAINER_PORT%
set PGUSER=%POSTGRES_USER%
set PGPASSWORD=%POSTGRES_PASSWORD%

REM SQL 파일 실행
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -f ".\create_tables.sql"
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -f ".\insert_cols_runnable_services.sql"
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -f ".\insert_cols_runnable_service_options.sql"

set PGHOST=
set PGPORT=
set PGUSER=
set PGPASSWORD=
pause