all:
	pyinstaller -F -w chaoxing.py
	copy ".\chaoxing_icon.ico" ".\dist\"
clean:
	-del /f /s /q "build"
	-del /f /s /q "dist"
	-rd /s /q "build"
	-rd /s /q "dist"
	-del "chaoxing.spec"
