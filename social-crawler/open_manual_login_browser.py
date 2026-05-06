#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


REPO_ROOT = pathlib.Path(__file__).resolve().parent
DEFAULT_PROFILE_DIR = REPO_ROOT / ".selenium-profile-meta"
DEFAULT_CHROME_BINARY = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DEFAULT_DRIVER = "/usr/local/bin/chromedriver"


def build_driver(profile_dir: pathlib.Path, chrome_binary: str, chromedriver: str, port: int) -> webdriver.Chrome:
    options = Options()
    options.binary_location = chrome_binary
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=Translate,OptimizationHints")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument(f"--remote-debugging-port={port}")
    options.add_experimental_option("detach", True)

    service = Service(executable_path=chromedriver)
    return webdriver.Chrome(service=service, options=options)


def main() -> int:
    parser = argparse.ArgumentParser(description="Open a visible Chrome window for manual Facebook/Threads login.")
    parser.add_argument("--profile-dir", default=str(DEFAULT_PROFILE_DIR))
    parser.add_argument("--chrome-binary", default=DEFAULT_CHROME_BINARY)
    parser.add_argument("--chromedriver", default=DEFAULT_DRIVER)
    parser.add_argument("--remote-debugging-port", type=int, default=9222)
    args = parser.parse_args()

    profile_dir = pathlib.Path(args.profile_dir).expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    for path in (args.chrome_binary, args.chromedriver):
        if not pathlib.Path(path).exists():
            missing.append(path)
    if missing:
        print("Missing required binary:", file=sys.stderr)
        for path in missing:
            print(f"  {path}", file=sys.stderr)
        return 1

    driver = build_driver(
        profile_dir=profile_dir,
        chrome_binary=args.chrome_binary,
        chromedriver=args.chromedriver,
        port=args.remote_debugging_port,
    )

    driver.get("https://www.facebook.com/login")
    driver.switch_to.new_window("tab")
    driver.get("https://www.threads.com/login")

    print("Opened visible Chrome for manual login.")
    print(f"Profile dir: {profile_dir}")
    print(f"Remote debugging port: {args.remote_debugging_port}")
    print("Log in manually, then keep this browser window open.")
    print("Press Ctrl+C here after you are done with the browser.")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nLeaving Chrome open for reuse.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
