import os
import random
from PIL import Image, ImageDraw, ImageFont

def generate_watermarked_images_and_annotations(
    symbol, backgrounds_dir, output_dir, font_path, 
    num_images=10, img_size=(640, 640), 
    rows_range=(3, 6), cols_range=(3, 6), font_size_range=(40, 75)
):
    """
    Generate watermarked images with variable configurations.

    Args:
        symbol (str): The symbol to overlay.
        backgrounds_dir (str): Directory containing background images.
        output_dir (str): Directory to save generated images and annotations.
        font_path (str): Path to the font file that supports the symbols.
        num_images (int): Number of images to generate.
        img_size (tuple): Size to which images will be resized (default: 640x640).
        rows_range (tuple): Range for the number of rows (min, max).
        cols_range (tuple): Range for the number of columns (min, max).
        font_size_range (tuple): Range for font size (min, max).
    """
    # Ensure the output directories exist
    images_dir = os.path.join(output_dir, "images")
    labels_dir = os.path.join(output_dir, "labels")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    # Load all background images
    background_files = [f for f in os.listdir(backgrounds_dir) if f.endswith(('jpg', 'png', 'jpeg'))]

    if not background_files:
        print("No background images found in the specified directory.")
        return

    for i in range(num_images):
        # Randomly select grid dimensions and font size
        rows = random.randint(*rows_range)
        cols = random.randint(*cols_range)
        font_size = random.randint(*font_size_range)

        # Randomly select a background image
        bg_file = random.choice(background_files)
        bg_path = os.path.join(backgrounds_dir, bg_file)
        background = Image.open(bg_path).convert("RGBA")

        # Resize the image to the desired size
        background = background.resize(img_size)

        # Create a drawable overlay
        width, height = background.size
        overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Calculate grid cell dimensions
        cell_width = width // cols
        cell_height = height // rows

        # Prepare annotation data
        annotations = []

        # Load the font
        font = ImageFont.truetype(font_path, font_size)

        for row in range(rows):
            for col in range(cols):
                # Calculate the position for the symbol
                x = col * cell_width + cell_width // 2
                y = row * cell_height + cell_height // 2

                # Measure the rendered symbol's size
                symbol_width, symbol_height = draw.textsize(symbol, font=font)

                # Offset to align symbol rendering
                text_x = x - symbol_width // 2
                vertical_offset = symbol_height // 4
                text_y = y - symbol_height // 2 - vertical_offset

                # Draw the symbol with fixed color and opacity
                fill_color = (128, 128, 128, 128)  # Fixed grey color with medium opacity
                draw.text((text_x, text_y), symbol, font=font, fill=fill_color)

                # Calculate bounding box values for YOLO annotation
                shrink_factor = 0.8
                w = (symbol_width / width) * shrink_factor
                h = (symbol_height / height) * shrink_factor
                x_center = x / width
                y_center = y / height

                annotations.append(f"2 {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")

        # Merge the overlay with the background
        watermarked = Image.alpha_composite(background, overlay)

        # Save the image
        img_output_path = os.path.join(images_dir, f"watermarkedtwo_{i+1}.jpg")
        watermarked.convert("RGB").save(img_output_path)

        # Save the annotations
        label_output_path = os.path.join(labels_dir, f"watermarkedtwo_{i+1}.txt")
        with open(label_output_path, "w") as label_file:
            label_file.write("\n".join(annotations))

        print(f"Saved: {img_output_path} and {label_output_path}")

if __name__ == "__main__":
    # Example usage
    symbol = "✈"  # Specify the symbol to overlay
    backgrounds_dir = "./backgrounds"  # Directory containing background images
    output_dir = "./output"  # Directory to save generated images and annotations
    font_path = "segoe-ui-symbol.ttf"  # Path to a font file that supports the symbol
    num_images = 100  # Number of images to generate

    generate_watermarked_images_and_annotations(
        symbol, backgrounds_dir, output_dir, font_path, num_images
    )
