@echo off

git pull origin main

git add .

git commit -m "."

git push -u origin main

REM 작업 완료 메시지 출력
echo Git Pushed!