import tempfile
import os
from shutil import rmtree, copy, make_archive

import shutil


folderName = os.path.basename(os.path.realpath("."))
tempPath = os.path.join(tempfile.gettempdir(), folderName)


try:
	rmtree(tempPath)
except (FileNotFoundError, NotADirectoryError):
	pass
try:
	rmtree(os.path.join("..", folderName + ".zip"))
except (FileNotFoundError, NotADirectoryError):
	pass
os.mkdir(tempPath)


excludeDirs = (
	".git",
	".vscode",
	"__pycache__"
)

for root, dirs, files in os.walk("."):
	dirs[:] = [d for d in dirs if d not in excludeDirs]
	for file in files:
		if file[-4:].lower() == ".pyc":
			continue
		if file.lower() in (".gitignore", ".gitattributes", "makezip.py"):
			continue

		src = os.path.normpath(os.path.join(root, file))
		dest = os.path.normpath(os.path.join(tempPath, folderName, root, file))
		os.makedirs(os.path.dirname(dest), exist_ok=True)
		print(src, dest)
		copy(src, dest)

make_archive(os.path.join("..", folderName), "zip", tempPath)
