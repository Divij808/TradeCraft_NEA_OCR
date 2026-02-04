import pyautogui

# Capture the current screen as a PIL image.
screenshot = pyautogui.screenshot()
# Persist the screenshot to disk for later review.
screenshot.save("my_screenshot.png")
# Display the screenshot in the default image viewer.
screenshot.show()
