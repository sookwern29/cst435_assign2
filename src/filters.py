import cv2
import numpy as np

def grayscale(img):
    """Convert RGB image to grayscale"""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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

def adjust_brightness(img, value=30):
    """Adjust image brightness"""
    return cv2.convertScaleAbs(img, alpha=1.0, beta=value)
