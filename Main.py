import os
import signal
import socket # checks the port
import subprocess # starts Brave
from pathlib import Path # handles .env
from time import sleep # adds delays

from playwright.sync_api import sync_playwright

from automation.Config import (
    CDP_URL,
    MAX_RETRIES,
    PROMPT_FILE,
    PROMPT_TEXTAREA_XPATH,
    RUN_BUTTON_XPATH,
    SELECT_IMAGE_MODEL_XPATH,
    SELECT_MODEL_MENU_XPATH,
    TARGET_URL,
    TEMP_CHAT_BUTTON_XPATH,
)
from automation.ImageWorkflow import download_generated_image, open_generated_image
from automation.ServerError import reload_if_error


ENV_FILE = Path(".env")


def run_workflow():
    prompt_text = read_prompt_text()
    retry_count = 0

    settings = load_env_settings()
    brave_process = ensure_browser_running(settings)
    browser = None

    try:
        with sync_playwright() as p:
            # Reuse the already-running browser instead of launching a new session.
            browser = p.chromium.connect_over_cdp(CDP_URL)
            log_message("Connected to the browser session.")

            if not browser.contexts:
                raise RuntimeError("No browser contexts were found on the attached browser.")

            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            while True:
                # Each pass starts from the prompt page so a failed attempt does not
                # leave us in a partially completed UI state.
                page.goto(TARGET_URL, wait_until="load", timeout=60000)
                page.bring_to_front()
                log_message("Opened AI Studio.")

                page.locator(f"xpath={SELECT_MODEL_MENU_XPATH}").click(timeout=60000)
                page.locator(f"xpath={SELECT_IMAGE_MODEL_XPATH}").click(timeout=60000)
                log_message("Selected the image model.")

                prompt_box = page.locator(f"xpath={PROMPT_TEXTAREA_XPATH}")
                prompt_box.wait_for(state="visible", timeout=60000)
                prompt_box.fill(prompt_text)
                log_message("Entered the prompt.")

                page.locator(f"xpath={RUN_BUTTON_XPATH}").click(timeout=60000)
                log_message("Started image generation.")

                # The product occasionally shows a temporary chat prompt before the
                # generated image is exposed.
                sleep(5)
                popup_button = page.locator(f"xpath={TEMP_CHAT_BUTTON_XPATH}")
                try:
                    popup_button.wait_for(state="visible", timeout=3000)
                    popup_button.click(timeout=60000)
                    log_message("Closed the temporary chat prompt.")
                except Exception:
                    pass

                sleep(8)
                log_message("Checked whether the image is ready.")

                if reload_if_error(page):
                    retry_count += 1
                    log_message(f"Internal error detected. Retry {retry_count} of {MAX_RETRIES}.")

                    if retry_count >= MAX_RETRIES:
                        log_message("Retry limit reached. Stopping the workflow.")
                        return

                    continue

                try:
                    # The image opens in a dialog first; the actual file comes from
                    # the browser download action inside that dialog.
                    open_generated_image(page)
                    log_message("Opened the generated image.")
                    saved_path = download_generated_image(page)
                    log_message(f"Saved the image to {saved_path}.")
                    retry_count = 0
                    break
                except Exception:
                    if reload_if_error(page):
                        retry_count += 1
                        log_message(f"Internal error detected. Retry {retry_count} of {MAX_RETRIES}.")

                        if retry_count >= MAX_RETRIES:
                            log_message("Retry limit reached. Stopping the workflow.")
                            return

                        continue
                    raise

            log_message("Image generation completed successfully.")
    finally:
        close_browser(browser)
        stop_brave(brave_process)


def log_message(message):
    print(message)


def main():
    run_workflow()


def read_prompt_text():
    prompt_text = PROMPT_FILE.read_text(encoding="utf-8").strip()
    if not prompt_text:
        raise ValueError(f"{PROMPT_FILE} is empty.")
    return prompt_text


def load_env_settings():
    if not ENV_FILE.exists():
        raise FileNotFoundError(".env file is missing.")

    settings = {}

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip().strip('"').strip("'")

    required_keys = [
        "BRAVE_BROWSER_PATH",
        "BRAVE_REMOTE_DEBUGGING_PORT",
        "BRAVE_PROFILE_DIRECTORY",
    ]
    missing_keys = [key for key in required_keys if key not in settings or not settings[key]]
    if missing_keys:
        raise ValueError(f".env is missing required values: {', '.join(missing_keys)}")

    return settings


def ensure_browser_running(settings):
    port = int(settings["BRAVE_REMOTE_DEBUGGING_PORT"])
    if port_is_open(port):
        return None

    command = [
        settings["BRAVE_BROWSER_PATH"],
        f"--remote-debugging-port={port}",
        f'--profile-directory={settings["BRAVE_PROFILE_DIRECTORY"]}',
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    for _ in range(30):
        if port_is_open(port):
            return process
        sleep(1)

    raise RuntimeError(f"Brave did not open remote debugging port {port}.")


def port_is_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def close_browser(browser):
    if browser is None:
        return

    try:
        browser.close()
    except Exception:
        pass


def stop_brave(process):
    if process is None:
        return

    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except Exception:
        try:
            process.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()
