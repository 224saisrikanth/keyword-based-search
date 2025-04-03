import os
from PIL import Image, ImageDraw, ImageFont

# Create favicon directory
os.makedirs('static/favicon', exist_ok=True)

# Colors
PRIMARY_COLOR = (67, 97, 238)  # #4361ee - your primary color
WHITE = (255, 255, 255)

def create_icon(size):
    # Create a blank image with the primary color
    img = Image.new('RGB', (size, size), PRIMARY_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw a magnifying glass icon
    padding = size // 4
    circle_size = size - (padding * 2)
    
    # Draw circle (lens of magnifying glass)
    draw.ellipse(
        (padding, padding, size - padding - (circle_size // 3), size - padding - (circle_size // 3)), 
        outline=WHITE, 
        width=max(1, size // 16)
    )
    
    # Draw handle
    handle_width = max(1, size // 12)
    handle_start_x = size - padding - (circle_size // 4)
    handle_start_y = size - padding - (circle_size // 4)
    draw.line(
        (handle_start_x, handle_start_y, size - (padding // 2), size - (padding // 2)), 
        fill=WHITE, 
        width=handle_width
    )
    
    return img

# Create icons in different sizes
icon_sizes = {
    'favicon-16x16.png': 16,
    'favicon-32x32.png': 32,
    'apple-touch-icon.png': 180,
    'android-chrome-192x192.png': 192,
    'android-chrome-512x512.png': 512
}

for filename, size in icon_sizes.items():
    icon = create_icon(size)
    icon.save(f'static/favicon/{filename}')
    print(f"Created {filename}")

# Create .ico file (needed for IE and some other browsers)
favicon = create_icon(32)
favicon.save('static/favicon/favicon.ico', format='ICO')
print("Created favicon.ico")

print("All favicon files created successfully!") 