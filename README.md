# KIT-AI-Studio

Automation for generating an image in Google AI Studio through Playwright, downloading the result, and saving it under `output/Generated Images`.

## Project Layout

- `Main.py`: entry point and workflow orchestration
- `automation/Config.py`: URLs, file paths, and XPath selectors
- `automation/ImageWorkflow.py`: opens the generated image dialog and downloads the file
- `automation/ServerError.py`: detects known page errors and reloads the page
- `.env`: Brave browser launch settings
- `Prompts.txt`: prompt text sent to AI Studio

## What The Script Does

The script:

1. Reads the prompt from `Prompts.txt`
2. Reads Brave launch settings from `.env`
3. Starts Brave with remote debugging if it is not already running
4. Connects Playwright to the existing browser session
5. Opens Google AI Studio
6. Selects the image model
7. Fills the prompt box
8. Runs generation
9. Handles the temporary chat prompt if it appears
10. Checks whether the generated image is ready
11. Detects known error messages and retries up to 3 times
12. Opens the generated image
13. Downloads the image into `output/Generated Images`
14. Closes the browser cleanly when the workflow finishes or fails

## How `Main.py` Works

`Main.py` is the only file you run directly.

It contains four main responsibilities:

- browser startup
- browser attachment
- generation retry loop
- cleanup

### Browser Startup

`Main.py` reads `.env` and launches Brave with the configured command if the debugging port is not open.

Relevant settings:

- `BRAVE_BROWSER_PATH`
- `BRAVE_REMOTE_DEBUGGING_PORT`
- `BRAVE_PROFILE_DIRECTORY`

If the port is already open, the script reuses the existing Brave session instead of launching a second browser.

### Retry Logic

The workflow retries only when the page contains one of these messages:

- `An internal error has occurred`
- `Content blocked`

The retry limit is 3 consecutive failures.

If the limit is reached, the script stops the workflow and exits cleanly.

### Cleanup

At the end of the run, the script always:

- closes the Playwright browser connection
- terminates the Brave process it started, if it launched one

This is handled in a `finally` block so cleanup still runs if the workflow fails.

## `automation/Config.py`

This file centralizes the stable configuration values:

- AI Studio URL
- CDP URL
- prompt file path
- XPath selectors
- output folder path
- retry limit

Keeping selectors here makes the automation easier to maintain because the page-specific values are in one place.

## `automation/ImageWorkflow.py`

This module contains the image-specific actions:

### `open_generated_image(page)`

Finds the newest result turn that contains an image and clicks it.

The code avoids a hardcoded turn id because AI Studio changes turn ids every run.

### `download_generated_image(page)`

Clicks the dialog download button, captures the Playwright download object, and saves the file into:

- `output/Generated Images`

If the folder already exists, it is reused.

## `automation/ServerError.py`

This module checks the rendered page text for known failure messages and reloads the page when one is present.

It is intentionally small because it represents a single rule:

- inspect the page text
- reload if an error message appears

## Output

Downloaded images are saved under:

```text
output/Generated Images/
```

Each run keeps the browser download filename suggested by the browser.

## Requirements

- Python 3.11
- Playwright
- Brave Browser installed at the path configured in `.env`

## Running

The automation is launched through the project task configuration:

```bash
python Main.py
```

If you use the existing task runner, `robot.yaml` already points to `Main.py`.

## `.env` Example

```env
BRAVE_BROWSER_PATH=/Applications/Brave Browser.app/Contents/MacOS/Brave Browser
BRAVE_REMOTE_DEBUGGING_PORT=9222
BRAVE_PROFILE_DIRECTORY=Profile 3
```

## Brave Launch Commands

If another person runs this project on a different device, they should update the Brave path and profile name to match their system.

### macOS

```bash
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  --remote-debugging-port=9222 \
  --profile-directory="Profile 3"
```

### Windows

```bat
"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" ^
  --remote-debugging-port=9222 ^
  --profile-directory="Profile 3"
```

### Linux

```bash
brave-browser \
  --remote-debugging-port=9222 \
  --profile-directory="Profile 3"
```

The important part is that the command matches the Brave installation path and the profile directory on that device. The debug port should also match the value stored in `.env`.

## Notes For Maintenance

- Update selectors in `automation/Config.py` if AI Studio changes its DOM.
- Update retry behavior in `Main.py` if the site becomes slower or less stable.
- Update error detection in `automation/ServerError.py` if AI Studio changes the wording of its warnings.
- Keep the Brave launch settings in `.env` so the browser startup can be changed without editing the code.
