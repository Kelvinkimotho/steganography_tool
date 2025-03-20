from PIL import Image
import numpy as np
import os

# Convert text to binary
def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

# Convert binary to text
def binary_to_text(binary_str):
    chars = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
    return ''.join(chr(int(char, 2)) for char in chars if int(char, 2) != 0)

# Convert non-PNG images to PNG
def convert_to_png(image_path):
    image = Image.open(image_path)
    new_path = os.path.splitext(image_path)[0] + ".png"
    image.convert("RGB").save(new_path, "PNG")
    return new_path  # Return new PNG path

# Hide message in an image
def hide_message(image_path, message, output_path):
    # Convert image to PNG if it's not already
    if not image_path.lower().endswith(".png"):
        image_path = convert_to_png(image_path)

    image = Image.open(image_path)
    image = image.convert("RGB")
    data = np.array(image)

    binary_message = text_to_binary(message) + '1111111111111110'  # End marker
    binary_index = 0

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(3):  # R, G, B channels
                if binary_index < len(binary_message):
                    data[i, j, k] = (data[i, j, k] & ~1) | int(binary_message[binary_index])
                    binary_index += 1

    stego_image = Image.fromarray(data)
    stego_image.save(output_path)

# Extract hidden message from an image
def extract_message(image_path):
    # Convert image to PNG if it's not already
    if not image_path.lower().endswith(".png"):
        image_path = convert_to_png(image_path)

    image = Image.open(image_path)
    data = np.array(image)

    binary_message = ""
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(3):  # R, G, B channels
                binary_message += str(data[i, j, k] & 1)

    end_marker = '1111111111111110'
    binary_message = binary_message[:binary_message.find(end_marker)] 

    return binary_to_text(binary_message)
