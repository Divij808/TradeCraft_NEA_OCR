import cv2

# Load image
image = cv2.imread("login_page.png")  # replace with your image path

# Check image loaded
if image is None:
    raise FileNotFoundError("Image not found. Check the file path.")

# ---------------------------
# Draw usability annotations
# ---------------------------

# Username field
cv2.rectangle(image, (120, 180), (480, 230), (0, 255, 0), 2)
cv2.arrowedLine(image, (500, 205), (480, 205), (255, 0, 0), 2)
cv2.putText(
    image,
    "Username field - clear label improves usability",
    (510, 210),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (0, 0, 0),
    1,
    cv2.LINE_AA
)

# Password field
cv2.rectangle(image, (120, 250), (480, 300), (0, 255, 0), 2)
cv2.arrowedLine(image, (500, 275), (480, 275), (255, 0, 0), 2)
cv2.putText(
    image,
    "Password field - masked input for security",
    (510, 280),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (0, 0, 0),
    1,
    cv2.LINE_AA
)

# Login button
cv2.rectangle(image, (200, 330), (400, 380), (0, 255, 0), 2)
cv2.arrowedLine(image, (420, 355), (400, 355), (255, 0, 0), 2)
cv2.putText(
    image,
    "Large login button - easy to identify",
    (430, 360),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (0, 0, 0),
    1,
    cv2.LINE_AA
)

# Forgot password link
cv2.rectangle(image, (250, 395), (420, 420), (0, 255, 0), 2)
cv2.arrowedLine(image, (440, 410), (420, 410), (255, 0, 0), 2)
cv2.putText(
    image,
    "Forgot password link improves recovery",
    (450, 415),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (0, 0, 0),
    1,
    cv2.LINE_AA
)

# ---------------------------
# Save annotated image
# ---------------------------
cv2.imwrite("login_page_annotated.png", image)

print("Annotated image saved as login_page_annotated.png")
