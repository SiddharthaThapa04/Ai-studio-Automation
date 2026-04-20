INTERNAL_ERROR_TEXT = "An internal error has occurred"
CONTENT_BLOCKED_TEXT = "Content blocked"


def reload_if_error(page):
    try:
        # Read the rendered page text and reload only if one of the known
        # failure messages is present.
        page_text = page.locator("body").inner_text(timeout=5000)
        if INTERNAL_ERROR_TEXT in page_text or CONTENT_BLOCKED_TEXT in page_text:
            page.reload(wait_until="load", timeout=60000)
            page.bring_to_front()
            return True
    except Exception:
        pass

    return False
