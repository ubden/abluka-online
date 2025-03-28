from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a new image with a transparent background
    size = 256
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Colors
    bg_color = (36, 39, 41, 255)  # Dark gray background
    gold = (255, 215, 0, 255)    # Gold for accents
    red = (220, 53, 69, 255)     # Red for obstacles
    black = (0, 0, 0, 255)       # Black piece
    white = (255, 255, 255, 255) # White piece
    
    # Draw circular background
    radius = size // 2 - 1
    draw.ellipse((1, 1, size - 2, size - 2), fill=bg_color, outline=gold, width=3)
    
    # Draw game pieces
    
    # Black piece
    black_piece_center = (size // 3, size // 2)
    black_radius = size // 6
    # Shadow
    draw.ellipse((
        black_piece_center[0] - black_radius + 3,
        black_piece_center[1] - black_radius + 3,
        black_piece_center[0] + black_radius + 3,
        black_piece_center[1] + black_radius + 3
    ), fill=(50, 50, 50, 255))
    # Piece
    draw.ellipse((
        black_piece_center[0] - black_radius,
        black_piece_center[1] - black_radius,
        black_piece_center[0] + black_radius,
        black_piece_center[1] + black_radius
    ), fill=black, outline=(70, 70, 70, 255), width=2)
    # Highlight
    highlight_radius = black_radius // 4
    draw.ellipse((
        black_piece_center[0] - black_radius // 2,
        black_piece_center[1] - black_radius // 2,
        black_piece_center[0] - black_radius // 2 + highlight_radius * 2,
        black_piece_center[1] - black_radius // 2 + highlight_radius * 2
    ), fill=(70, 70, 70, 255))
    
    # White piece
    white_piece_center = (2 * size // 3, size // 2)
    white_radius = size // 6
    # Shadow
    draw.ellipse((
        white_piece_center[0] - white_radius + 3,
        white_piece_center[1] - white_radius + 3,
        white_piece_center[0] + white_radius + 3,
        white_piece_center[1] + white_radius + 3
    ), fill=(50, 50, 50, 255))
    # Piece
    draw.ellipse((
        white_piece_center[0] - white_radius,
        white_piece_center[1] - white_radius,
        white_piece_center[0] + white_radius,
        white_piece_center[1] + white_radius
    ), fill=white, outline=black, width=2)
    # Inner rim
    draw.ellipse((
        white_piece_center[0] - white_radius + 5,
        white_piece_center[1] - white_radius + 5,
        white_piece_center[0] + white_radius - 5,
        white_piece_center[1] + white_radius - 5
    ), outline=(200, 200, 200, 255), width=1)
    # Highlight
    highlight_radius = white_radius // 4
    draw.ellipse((
        white_piece_center[0] - white_radius // 2,
        white_piece_center[1] - white_radius // 2,
        white_piece_center[0] - white_radius // 2 + highlight_radius * 2,
        white_piece_center[1] - white_radius // 2 + highlight_radius * 2
    ), fill=white)
    
    # Red obstacle
    obstacle_center = (size // 2, size // 2 - size // 4)
    obstacle_size = size // 8
    # Shadow
    draw.rectangle((
        obstacle_center[0] - obstacle_size // 2 + 3,
        obstacle_center[1] - obstacle_size // 2 + 3,
        obstacle_center[0] + obstacle_size // 2 + 3,
        obstacle_center[1] + obstacle_size // 2 + 3
    ), fill=(50, 20, 20, 255))
    # Obstacle
    draw.rectangle((
        obstacle_center[0] - obstacle_size // 2,
        obstacle_center[1] - obstacle_size // 2,
        obstacle_center[0] + obstacle_size // 2,
        obstacle_center[1] + obstacle_size // 2
    ), fill=red, outline=(150, 0, 0, 255), width=2)
    # Highlight
    highlight_size = obstacle_size // 3
    draw.rectangle((
        obstacle_center[0] - obstacle_size // 2 + 3,
        obstacle_center[1] - obstacle_size // 2 + 3,
        obstacle_center[0] - obstacle_size // 2 + 3 + highlight_size,
        obstacle_center[1] - obstacle_size // 2 + 3 + highlight_size
    ), fill=(255, 100, 100, 180))
    
    # Save as different sizes for ICO file
    icon_dir = 'assets'
    os.makedirs(icon_dir, exist_ok=True)
    
    # Save as PNG first
    icon_path = os.path.join(icon_dir, 'icon.png')
    icon.save(icon_path)
    
    # Convert to ICO using PIL
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []
    for size in icon_sizes:
        icons.append(icon.resize(size, Image.LANCZOS))
    
    # Save the ICO file
    ico_path = os.path.join(icon_dir, 'icon.ico')
    icons[0].save(ico_path, format='ICO', sizes=[(i.width, i.height) for i in icons])
    
    print("Icon files created successfully!")

if __name__ == "__main__":
    create_icon() 