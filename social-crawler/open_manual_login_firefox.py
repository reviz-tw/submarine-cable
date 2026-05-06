#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import sys
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


REPO_ROOT = pathlib.Path(__file__).resolve().parent
DEFAULT_PROFILE_DIR = REPO_ROOT / ".selenium-profile-firefox"
DEFAULT_FIREFOX_BINARY = "/Applications/Firefox.app/Contents/MacOS/firefox"
DEFAULT_DRIVER = "/usr/local/Cellar/geckodriver/0.36.0/bin/geckodriver"


def main() -> int:
    profile_dir = DEFAULT_PROFILE_DIR
    profile_dir.mkdir(parents=True, exist_ok=True)

    for path in (DEFAULT_FIREFOX_BINARY, DEFAULT_DRIVER):
        if not pathlib.Path(path).exists():
            print(f"Missing required binary: {path}", file=sys.stderr)
            return 1

    options = Options()
    options.binary_location = DEFAULT_FIREFOX_BINARY
    options.add_argument("-profile")
    options.add_argument(str(profile_dir))
    options.add_argument("-no-remote")

    service = Service(executable_path=DEFAULT_DRIVER)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_position(80, 80)
    driver.set_window_size(1320, 900)

    driver.get("https://www.facebook.com/login")
    driver.switch_to.new_window("tab")
    driver.get("https://www.threads.com/login")

    print("Opened visible Firefox for manual login.")
    print(f"Profile dir: {profile_dir}")
    print("Log in manually, keep Firefox open, and tell me when you're done.")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nLeaving Firefox open for reuse.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
