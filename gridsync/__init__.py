"""Synchronize local directories with Tahoe-LAFS storage grids."""

import os
import sys

from gridsync._version import get_versions
from gridsync.config import Config

__author__ = "Christopher R. Wood"
__url__ = "https://github.com/gridsync/gridsync"
__license__ = "GPLv3"
__version__ = get_versions()['version']


if getattr(sys, "frozen", False):
    pkgdir = os.path.dirname(os.path.realpath(sys.executable))
    os.environ["PATH"] += os.pathsep + os.path.join(pkgdir, "Tahoe-LAFS")
    if sys.platform == "win32" and getattr(sys, "_MEIPASS", False):
        # Workaround for PyInstaller being unable to find Qt5Core.dll on PATH.
        # See https://github.com/pyinstaller/pyinstaller/issues/4293
        os.environ["PATH"] = sys._MEIPASS + os.pathsep + os.environ["PATH"]  # type: ignore
    try:
        del sys.modules["twisted.internet.reactor"]  # PyInstaller workaround
    except KeyError:
        pass
    if sys.platform not in ("win32", "darwin"):
        # PyInstaller's bootloader sets the 'LD_LIBRARY_PATH' environment
        # variable to the root of the executable's directory which causes
        # `xdg-open` -- and, by extension, QDesktopServices.openUrl() -- to
        # fail to properly locate/launch applications by MIME-type/URI-handler.
        # Unsetting it globally here fixes this issue.
        os.environ.pop("LD_LIBRARY_PATH", None)
else:
    pkgdir = os.path.dirname(os.path.realpath(__file__))


settings = Config(os.path.join(pkgdir, "resources", "config.txt")).load()

try:
    APP_NAME = settings["application"]["name"]
except KeyError:
    APP_NAME = "Gridsync"

if sys.platform == "win32":
    appdata = str(os.getenv("APPDATA"))
    config_dir = os.path.join(appdata, APP_NAME)
    autostart_file_path = os.path.join(
        appdata,
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
        APP_NAME + ".lnk",
    )
elif sys.platform == "darwin":
    config_dir = os.path.join(
        os.path.expanduser("~"), "Library", "Application Support", APP_NAME
    )
    autostart_file_path = os.path.join(
        os.path.expanduser("~"), "Library", "LaunchAgents", APP_NAME + ".plist"
    )
else:
    config_home = os.environ.get(
        "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
    )
    config_dir = os.path.join(config_home, APP_NAME.lower())
    autostart_file_path = os.path.join(
        config_home, "autostart", APP_NAME + ".desktop"
    )


def resource(filename):
    return os.path.join(pkgdir, "resources", filename)


if getattr(sys, "frozen", False):
    try:
        with open(resource("version.txt")) as f:
            __version__ = f.read()
    except OSError:
        pass
