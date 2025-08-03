@echo off
echo ========================================
echo BASED GOD CODER CLI - GitHub Setup
echo Made by @Lucariolucario55 on Telegram
echo ========================================
echo.

echo Step 1: Initializing Git Repository...
git init
if %errorlevel% neq 0 (
    echo Error: Git initialization failed
    pause
    exit /b 1
)

echo.
echo Step 2: Adding all files to Git...
git add .
if %errorlevel% neq 0 (
    echo Error: Git add failed
    pause
    exit /b 1
)

echo.
echo Step 3: Creating initial commit...
git commit -m "🔥 Initial release of BASED GOD CODER CLI - Made by @Lucariolucario55"
if %errorlevel% neq 0 (
    echo Error: Git commit failed
    pause
    exit /b 1
)

echo.
echo Step 4: Setting main branch...
git branch -M main
if %errorlevel% neq 0 (
    echo Warning: Could not set main branch (may already exist)
)

echo.
echo ========================================
echo SUCCESS! Git repository is ready!
echo ========================================
echo.
echo Next steps:
echo 1. Create a new repository on GitHub.com
echo 2. Copy the repository URL
echo 3. Run the following commands:
echo.
echo    git remote add origin YOUR_REPO_URL
echo    git push -u origin main
echo.
echo Example:
echo    git remote add origin https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI.git
echo    git push -u origin main
echo.

echo Repository URL examples:
echo - HTTPS: https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI.git
echo - SSH:   git@github.com:YOUR_USERNAME/BASED-GOD-CODER-CLI.git
echo.

echo ========================================
echo Files ready for GitHub:
echo ========================================
dir /b *.md *.txt *.py *.bat *.cmd *.json LICENSE
echo.

echo Current git status:
git status --short
echo.

echo Do you want to add a remote repository now? (y/n)
set /p choice=Enter your choice: 
if /i "%choice%"=="y" (
    set /p repo_url=Enter your GitHub repository URL: 
    git remote add origin %repo_url%
    echo.
    echo Repository URL added! Now run:
    echo git push -u origin main
    echo.
    echo Do you want to push now? (y/n)
    set /p push_choice=Enter your choice: 
    if /i "%push_choice%"=="y" (
        git push -u origin main
        echo.
        echo ========================================
        echo SUCCESS! BASED GOD CODER CLI is now on GitHub!
        echo ========================================
    )
)

echo.
pause