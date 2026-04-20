# KIT-AI-Studio

Automates image generation in Google AI Studio through Playwright, downloads the generated image, and saves it under `output/Generated Images`.

## Current Structure

- `Main.py`: entry point and workflow orchestration
- `automation/Config.py`: URLs, file paths, and XPath selectors
- `automation/ImageWorkflow.py`: opens the generated image dialog and downloads the file
- `automation/ServerError.py`: detects known page error text and reloads the page
- `.env`: Brave browser path and profile settings
- `Prompts.txt`: prompt text sent to AI Studio

## Execution Flow

1. `robot.yaml` runs `python Main.py`
2. `Main.py` reads the prompt from `Prompts.txt`
3. `Main.py` reads Brave settings from `.env`
4. `Main.py` checks whether the Brave debug port `9222` is already open
5. If Brave is not running, `Main.py` launches it with remote debugging enabled
6. Playwright connects to the running browser session
7. The script opens Google AI Studio
8. The script selects the image model
9. The script fills the prompt box
10. The script clicks Run
11. The script handles the temporary chat prompt if it appears
12. The script waits for the response
13. If an error message appears, the page reloads and the workflow retries
14. If the rate limit message appears, the workflow stops immediately
15. If generation succeeds, the generated image is opened and downloaded
16. Cleanup always runs at the end

## `Main.py`

`Main.py` owns the full workflow.

### Browser Startup

`Main.py` reads `.env` for:

- `BRAVE_BROWSER_PATH`
- `BRAVE_PROFILE_DIRECTORY`

The remote debugging port is hardcoded in the script as `9222`.

When Brave starts:

- if the requested profile folder exists, the script opens that profile
- if the profile name is empty or does not exist, the script falls back to Brave's default profile
- if Brave is already running on the debugging port, the script reuses it

### Retry Behavior

The workflow retries when the page contains:

- `An internal error has occurred`
- `Content blocked`

The retry limit is `3`.

If the page contains:

- `You've reached your rate limit. Please try again later.`

the workflow stops immediately and exits through the normal cleanup path.

### Cleanup

At the end of execution, `Main.py` always:

- closes the Playwright browser connection
- terminates the Brave process that was launched by the script

This happens in a `finally` block so cleanup still runs on success, retry exhaustion, or exceptions.

## `automation/Config.py`

This file stores the stable values used by the workflow:

- `TARGET_URL`
- `CDP_URL`
- `PROMPT_FILE`
- selectors for the model menu, image model, prompt box, run button, and generated image
- download folder path
- retry limit

Keeping these values together makes it easier to update the automation when the AI Studio DOM changes.

## `automation/ImageWorkflow.py`

This module handles the image-specific steps.

### `open_generated_image(page)`

This function:

- finds the newest turn that contains an image
- clicks the image or its nearest clickable wrapper

It avoids hardcoded turn ids because AI Studio changes them every run.

### `download_generated_image(page)`

This function:

- clicks the download button in the image dialog
- captures the browser download
- saves the file into `output/Generated Images`

If the folder already exists, it is reused.

## `automation/ServerError.py`

This module checks the rendered page text for known messages and decides whether to reload or stop.

It currently recognizes:

- `An internal error has occurred`
- `Content blocked`
- `You've reached your rate limit. Please try again later.`

The first two messages trigger a page reload through `Main.py`.
The rate-limit message stops the workflow immediately.

## Output

Generated images are saved under:

```text
output/Generated Images/
```

The saved filename comes from the browser download.

## Requirements

- Python 3.11
- Playwright
- Brave Browser installed on the machine

## `.env`

This file is used for Brave startup only.

Example:

```env
BRAVE_BROWSER_PATH=/path/to/Brave Browser executable
BRAVE_PROFILE_DIRECTORY=Profile 3
```

If `BRAVE_PROFILE_DIRECTORY` is empty or the named profile does not exist, the script falls back to Brave's default profile.

## Brave Launch Command

The browser is launched internally by `Main.py`, but this is the equivalent manual command:

### macOS

```bash
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  --remote-debugging-port=9222 \
  --profile-directory=""
```

### Windows

```bat
"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" ^
  --remote-debugging-port=9222 ^
  --profile-directory=""
```

### Linux

```bash
brave-browser \
  --remote-debugging-port=9222 \
  --profile-directory=""
```

If the profile name does not exist, Brave opens the default profile instead.

## Running

The project task runner already points to `Main.py`:

```bash
python Main.py
```

## Maintenance Notes

- Update selectors in `automation/Config.py` if AI Studio changes its DOM.
- Update error text handling in `automation/ServerError.py` if the warning messages change.
- Update `Main.py` if the Brave startup command or profile selection logic changes.
