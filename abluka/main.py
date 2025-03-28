import sys
import pygame
import argparse
from abluka.gui import AblukaGUI

def main():
    # Parse command line arguments for window size only
    parser = argparse.ArgumentParser(description='Abluka PC-  Ubden® Akademi PC Zeka Oyunu')
    parser.add_argument('--width', type=int, default=800,
                        help='Window width')
    parser.add_argument('--height', type=int, default=800,
                        help='Window height')
    
    args = parser.parse_args()
    
    # Create and run the game with menu
    game = AblukaGUI(
        width=args.width,
        height=args.height
    )
    
    print("Starting Abluka - Choose game mode from the menu")
    game.run()

if __name__ == "__main__":
    main() 