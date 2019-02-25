from shutil import rmtree, copytree
import os
from urllib.parse import urlparse
from urllib.request import urlretrieve, build_opener, install_opener
from tempfile import gettempdir


targetPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")

urlList = (
	"https://cdn.jsdelivr.net/npm/leaflet@1.4.0/dist/leaflet.css",
	"https://cdn.jsdelivr.net/npm/leaflet@1.4.0/dist/leaflet-src.min.js",
	"https://cdn.jsdelivr.net/npm/leaflet.fullscreen@1.4.5/Control.FullScreen.css",
	"https://cdn.jsdelivr.net/npm/leaflet.fullscreen@1.4.5/Control.FullScreen.min.js",
	"https://cdn.jsdelivr.net/npm/jquery@3.3.1/dist/jquery.min.js",
	"https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css",
	"https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js",
	"https://cdn.jsdelivr.net/gh/L0laapk3/Leaflet.OpacityControls@1/Control.Opacity.css",
	"https://cdn.jsdelivr.net/gh/L0laapk3/Leaflet.OpacityControls@1/Control.Opacity.js",
	"https://factorio.com/static/img/favicon.ico",
	"https://i.factoriomaps.com/t92kw.png",
)



tempPath = os.path.join(gettempdir(), "FactorioMapsTmpLib")
try:
	rmtree(tempPath)
except (FileNotFoundError, NotADirectoryError):
	pass

os.makedirs(tempPath, exist_ok=True)


opener = build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 U GUYS SUCK WHY ARE YOU BLOCKING Python-urllib')]
install_opener(opener)

for url in urlList:
	print(f"downloading {url}")
	urlretrieve(url, os.path.join(tempPath, os.path.basename(urlparse(url).path)))


	
try:
	rmtree(targetPath)
except (FileNotFoundError, NotADirectoryError):
	pass


copytree(tempPath, targetPath)
with open(os.path.join(targetPath, "VERSION"), "w") as f:
	f.write("1")


try:
	rmtree(tempPath)
except (FileNotFoundError, NotADirectoryError):
	pass