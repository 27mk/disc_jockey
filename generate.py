import json
import os
from PIL import Image, ImageDraw, ImageFont
import time
import random

# Drawing dimension constants
width, height = 4000, 4000
center = (width // 2, height // 2)
outer_radius = 1800
inner_radius = 600

def load_album_data(json_path):
    print("Loading album data from JSON file...")
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} albums.")
        return data
    except Exception as e:
        print(f"Error loading album data: {e}")
        return []

def generate_image_for_album(album_id, tracklist):
    print(f"Generating image for album ID: {album_id}")
    try:
        # Debugging tracklist data
        print(f"Tracklist for album {album_id}: {tracklist}")

        # Load the album front image from the static folder
        sticker_path = f"static/{album_id}_front.jpg"
        if not os.path.exists(sticker_path):
            print(f"Album front image {sticker_path} not found, skipping.")
            return

        # Generate image for the album
        output_path = f"static/{album_id}_record.png"
        print(f"About to generate image for album and save it to {output_path}")

        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        color_dark = (0, 0, 0, 255)
        color_light = (10, 10, 10, 255)

        draw.pieslice(
            [center[0] - outer_radius, center[1] - outer_radius, center[0] + outer_radius, center[1] + outer_radius],
            0, 360, fill=color_dark
        )

        # Change this from being randomized to being based on JSON data
        current_radius = outer_radius
        while current_radius > inner_radius:
            track_width = random.randint(40, 100)  # Random varied width
            track_color = color_light if random.random() > 0.5 else color_dark  # Random selection of the two colors
            draw.pieslice(
                [center[0] - current_radius, center[1] - current_radius, center[0] + current_radius, center[1] + current_radius],
                0, 360, fill=track_color
            )
            current_radius -= track_width

        # Draw the lighter center area around the sticker
        draw.pieslice(
            [center[0] - inner_radius, center[1] - inner_radius, center[0] + inner_radius, center[1] + inner_radius],
            0, 360, fill=color_light
        )

        sticker_image = resize_and_crop_sticker(sticker_path, target_size=(2 * inner_radius, 2 * inner_radius))

        img.paste(sticker_image, (center[0] - inner_radius, center[1] - inner_radius), sticker_image)

        img.save(output_path)

        if os.path.exists(output_path):
            print(f"Image saved successfully for album {album_id} at {output_path}")
        else:
            print(f"Failed to save image for album {album_id} at {output_path}")

    except Exception as e:
        print(f"Error generating image for album {album_id}: {e}")

def process_album_data(album_data):
    for album in album_data:
        album_id = album.get("id")
        tracklist = album.get("tracklist", {})

        # Check if album data is missing tracklist or ID
        if not album_id:
            print(f"Skipping album with missing ID.")
            continue

        if not tracklist:
            print(f"Skipping album {album_id} with missing tracklist.")
            continue

        generate_image_for_album(album_id, tracklist)

# Function to resize and crop the sticker image
def resize_and_crop_sticker(sticker_path, target_size=(600, 600)):
    print(f"Resizing and cropping sticker: {sticker_path}")  # Debug print
    try:
        sticker = Image.open(sticker_path)
        sticker = sticker.resize(target_size, Image.LANCZOS)
        mask = Image.new('L', target_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, target_size[0], target_size[1]), fill=255)
        sticker.putalpha(mask)
        return sticker
    except Exception as e:
        print(f"Error resizing and cropping sticker: {e}")
        return None

def main():
    album_data = load_album_data('album_data.json')
    if album_data:
        process_album_data(album_data)
    else:
        print("No album data to process.")

if __name__ == "__main__":
    main()

