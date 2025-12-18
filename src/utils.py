import cv2
import os
from filters import (
    grayscale,
    gaussian_blur,
    sobel_edge,
    sharpen,
    adjust_brightness
)

def process_image(image_path, output_dir):
    """Apply full image processing pipeline to one image"""
    img = cv2.imread(image_path)

    if img is None:
        return

    img = grayscale(img)
    img = gaussian_blur(img)
    img = sobel_edge(img)
    img = sharpen(img)
    img = adjust_brightness(img)

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_dir, filename)

    cv2.imwrite(output_path, img)
