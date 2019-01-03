workon deploy-pyqt && ^
cls && ^
pyi-makespec "SVFB-GUI/Stardew Valley Fishing Bot.py" --noconsole -i "SVFB-GUI/media/logo/logo.ico" --add-data "SVFB-GUI/SVFBFuncs";"SVFBFuncs" --add-data "SVFB-GUI/designs";"designs" --add-data "SVFB-GUI/media";"media" --add-data "SVFB-GUI/config.json";"." && ^
cls && ^
echo "Success creating spec file" && ^
pyinstaller "Stardew Valley Fishing Bot.spec" && ^
mkdir "dist/Stardew Valley Fishing Bot/Data" && ^
mkdir "dist/Stardew Valley Fishing Bot/Data/Training Data" && ^
rd "build" /s/q && ^
echo "Success!"