from pathlib import Path


# Runtime endpoints and file locations.
TARGET_URL = "https://aistudio.google.com/prompts/new_chat"
CDP_URL = "http://127.0.0.1:9222"
PROMPT_FILE = Path("Prompts.txt")

# Stable selectors used by the automation flow.
SELECT_MODEL_MENU_XPATH = '//button[@data-test-category-id="15"]'
SELECT_IMAGE_MODEL_XPATH = '//button[@id="model-carousel-row-models/gemini-2.5-flash-image"]'
PROMPT_TEXTAREA_XPATH = (
    '//textarea[@placeholder="Start typing a prompt to see what our models can do"]'
)
RUN_BUTTON_XPATH = '//button[@type="submit" and .//span[normalize-space(text())="Run"]]'
GENERATED_TURN_SELECTOR = '[id^="turn-"]'
DOWNLOAD_BUTTON_XPATH = '//*[@id="mat-mdc-dialog-title-0"]/div[2]/button[1]/span'
GENERATED_IMAGES_DIR = Path("output") / "Generated Images"
MAX_RETRIES = 3
