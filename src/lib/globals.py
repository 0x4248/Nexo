import subprocess
from datetime import datetime

def get_git_ref():
	try:
		return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
	except subprocess.CalledProcessError:
		return "unknown"

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_REF = get_git_ref()
VERSION_TYPE = "beta"
VERSION_CODE = "Lonely Lancer"
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
VERSION_FULL = f"{VERSION}-{VERSION_REF} ({VERSION_TYPE}) {VERSION_CODE}"

START_TIME = datetime.now()
SERVER_NAME = "Nexo System"
SERVER_NAME_SHORT = "Nexo"
SERVER_ENGINE = "Nexo"