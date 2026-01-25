@echo off
echo Testing Automation Task API...
echo.

echo 1. Testing /automation/task/list
curl -X GET "http://localhost:9099/dev-api/automation/task/list?pageNum=1&pageSize=10" -H "Content-Type: application/json"
echo.
echo.

echo 2. Testing /automation/session/list (working module for comparison)
curl -X GET "http://localhost:9099/dev-api/automation/session/list?pageNum=1&pageSize=10" -H "Content-Type: application/json"
echo.
echo.

pause
