import cv2
import numpy as np

def grayscale(img):
    """Convert RGB image to grayscale using luminance formula"""
    # Luminance formula: Y = 0.299*R + 0.587*G + 0.114*B
    # Since OpenCV uses BGR, img[:, :, 0] is B, 1 is G, 2 is R
    gray = 0.299 * img[:, :, 2] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 0]
    return gray.astype(np.uint8)

def gaussian_blur(img):
    """Apply 3x3 Gaussian blur"""
    return cv2.GaussianBlur(img, (3, 3), 0)

def sobel_edge(img):
    """Apply Sobel edge detection"""
    grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(grad_x, grad_y)
    return cv2.convertScaleAbs(magnitude)

def sharpen(img):
    """Sharpen image"""
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

def adjust_brightness(img):
    """Adjust image brightness based on original image condition: increase if dark, decrease if bright"""
    # Compute average brightness
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    mean_brightness = np.mean(gray)
    if mean_brightness < 128:
        beta = 30  # increase brightness for dark images
    else:
        beta = -30  # decrease brightness for bright images
    return cv2.convertScaleAbs(img, alpha=1.0, beta=beta)
