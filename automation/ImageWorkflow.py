from automation.Config import DOWNLOAD_BUTTON_XPATH, GENERATED_IMAGES_DIR, GENERATED_TURN_SELECTOR


def open_generated_image(page):
    # Turn ids change on every run, so find the latest turn that contains an
    # image instead of relying on a hardcoded DOM id.
    generated_turn = page.locator(GENERATED_TURN_SELECTOR).filter(
        has=page.locator("img")
    ).last
    generated_turn.wait_for(state="visible", timeout=300000)
    generated_turn.scroll_into_view_if_needed(timeout=60000)

    image = generated_turn.locator("img").last
    image.wait_for(state="visible", timeout=60000)

    # If the image is wrapped in a clickable element, use that wrapper so the
    # dialog opens the same way a user click would.
    clickable_wrapper = image.locator(
        "xpath=ancestor::button[1] | ancestor::a[1] | ancestor::*[@role='button'][1]"
    )

    if clickable_wrapper.count() > 0:
        clickable_wrapper.first.click(timeout=60000)
        return

    image.click(timeout=60000)


def download_generated_image(page):
    download_button = page.locator(f"xpath={DOWNLOAD_BUTTON_XPATH}")
    download_button.wait_for(state="visible", timeout=60000)

    # Create the output folder only if it does not already exist.
    GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Capture the browser download directly and save it under output/.
    with page.expect_download(timeout=60000) as download_info:
        download_button.click(timeout=60000)

    download = download_info.value
    target_path = GENERATED_IMAGES_DIR / download.suggested_filename
    download.save_as(target_path)
    return target_path
