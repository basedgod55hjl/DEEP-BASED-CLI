@echo off
echo Setting up BASED GOD CODER CLI for GitHub...

:: Initialize git repository if not already initialized
git init

:: Add all files to git
git add .

:: Commit the initial version
git commit -m "🔥 Initial release of BASED GOD CODER CLI - Made by @Lucariolucario55"

:: Create main branch if needed
git branch -M main

echo.
echo Repository ready! Now you need to:
echo 1. Create a new repository on GitHub
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_REPO_URL
echo 4. Run: git push -u origin main
echo.
echo Example:
echo git remote add origin https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI.git
echo git push -u origin main
echo.
pause