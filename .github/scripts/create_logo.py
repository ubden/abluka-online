import math
import random

def create_svg():
    # SVG canvas dimensions
    width, height = 500, 500
    # Colors
    bg_color = "#242729"
    gold = "#FFD700"
    red = "#DC3545"
    black = "#000000"
    white = "#FFFFFF"
    
    # SVG header
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
    
    # Background with subtle gradient
    svg += f'<rect width="{width}" height="{height}" fill="{bg_color}" />\n'
    
    # Add subtle pattern to background
    for i in range(25):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(1, 3)
        opacity = random.uniform(0.05, 0.2)
        svg += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" fill-opacity="{opacity}" />\n'
    
    # Create a circular game board
    board_radius = 180
    board_cx, board_cy = width // 2, height // 2
    svg += f'<circle cx="{board_cx}" cy="{board_cy}" r="{board_radius}" fill="#F0F0F0" stroke="{gold}" stroke-width="3" />\n'
    
    # Add grid lines to the circular board
    for i in range(0, 360, 30):
        rad = math.radians(i)
        x1 = board_cx + math.cos(rad) * board_radius
        y1 = board_cy + math.sin(rad) * board_radius
        x2 = board_cx - math.cos(rad) * board_radius
        y2 = board_cy - math.sin(rad) * board_radius
        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#343A40" stroke-width="1" />\n'
    
    # Draw 3 concentric circles on the board
    for r in range(60, board_radius, 60):
        svg += f'<circle cx="{board_cx}" cy="{board_cy}" r="{r}" fill="none" stroke="#343A40" stroke-width="1" />\n'
    
    # Draw game pieces
    
    # Black piece with highlight and shadow
    black_piece_cx, black_piece_cy = board_cx - 80, board_cy - 10
    # Shadow
    svg += f'<circle cx="{black_piece_cx+3}" cy="{black_piece_cy+3}" r="35" fill="#333333" />\n'
    # Piece
    svg += f'<circle cx="{black_piece_cx}" cy="{black_piece_cy}" r="35" fill="{black}" />\n'
    # Highlight
    svg += f'<circle cx="{black_piece_cx-10}" cy="{black_piece_cy-10}" r="8" fill="#444444" />\n'
    # Rim
    svg += f'<circle cx="{black_piece_cx}" cy="{black_piece_cy}" r="35" fill="none" stroke="#444444" stroke-width="2" />\n'
    
    # White piece with highlight and shadow
    white_piece_cx, white_piece_cy = board_cx + 80, board_cy - 10
    # Shadow
    svg += f'<circle cx="{white_piece_cx+3}" cy="{white_piece_cy+3}" r="35" fill="#333333" />\n'
    # Piece
    svg += f'<circle cx="{white_piece_cx}" cy="{white_piece_cy}" r="35" fill="{white}" />\n'
    # Rim
    svg += f'<circle cx="{white_piece_cx}" cy="{white_piece_cy}" r="35" fill="none" stroke="{black}" stroke-width="2" />\n'
    # Inner rim
    svg += f'<circle cx="{white_piece_cx}" cy="{white_piece_cy}" r="30" fill="none" stroke="#CCCCCC" stroke-width="1" />\n'
    # Highlight
    svg += f'<circle cx="{white_piece_cx-10}" cy="{white_piece_cy-10}" r="8" fill="#FFFFFF" />\n'
    
    # Red obstacle with gradients
    for i in range(3):
        angle = i * 120 + 30
        rad = math.radians(angle)
        obstacle_cx = board_cx + math.cos(rad) * 120
        obstacle_cy = board_cy + math.sin(rad) * 120
        
        # Define gradient for red obstacle
        gradient_id = f"redGradient{i}"
        svg += f'<defs>\n'
        svg += f'  <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="0%" y2="100%">\n'
        svg += f'    <stop offset="0%" style="stop-color:#C42F36;stop-opacity:1" />\n'
        svg += f'    <stop offset="100%" style="stop-color:#AA0000;stop-opacity:1" />\n'
        svg += f'  </linearGradient>\n'
        svg += f'</defs>\n'
        
        # Shadow
        svg += f'<rect x="{obstacle_cx-15+3}" y="{obstacle_cy-15+3}" width="30" height="30" fill="#333333" />\n'
        # Obstacle
        svg += f'<rect x="{obstacle_cx-15}" y="{obstacle_cy-15}" width="30" height="30" fill="url(#{gradient_id})" stroke="#800000" stroke-width="2" />\n'
        # Highlight
        svg += f'<rect x="{obstacle_cx-13}" y="{obstacle_cy-13}" width="10" height="10" fill="#FF5555" fill-opacity="0.5" />\n'
    
    # Add title
    svg += f'<text x="{width//2}" y="70" font-family="Arial, sans-serif" font-size="50" font-weight="bold" fill="{gold}" text-anchor="middle">ABLUKA</text>\n'
    
    # Subtitle
    svg += f'<text x="{width//2}" y="110" font-family="Arial, sans-serif" font-size="18" fill="#CCCCCC" text-anchor="middle">Strateji Oyunu</text>\n'
    
    # Add emoji representation for AI
    svg += f'<text x="{black_piece_cx}" y="{black_piece_cy-50}" font-family="Arial, sans-serif" font-size="30" text-anchor="middle">🤔</text>\n'
    
    # Footer text
    svg += f'<text x="{width//2}" y="{height-30}" font-family="Arial, sans-serif" font-size="14" fill="#999999" text-anchor="middle">Abluka © Akıl ve Zeka Oyunları</text>\n'
    
    # Close SVG
    svg += '</svg>'
    
    # Write to file
    with open('abluka_logo.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    
    print("SVG logo created successfully!")

if __name__ == "__main__":
    create_svg() 