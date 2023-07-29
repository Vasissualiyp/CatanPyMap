# Code by Vasilii Pustovoit, 07/2023
# Original JavaScript code by dado3212, at https://github.com/dado3212/catan
# Library import {{{
import random
from typing import List
from PIL import Image, ImageDraw
import numpy as np
from helper import shuffle, encode64, decode64
from random import randint
import math
#}}}

# Variables definitions {{{
background_image_path = './large_assets/extracted/tiles/sea_tiles.png'
output_name = './game.png'

# Final image size
CANVAS_WIDTH = 3840
CANVAS_HEIGHT = 2160

# Tile properties
TILE_SIZE = int(40*6.4)  # size of each tile in pixels, 2xTILE_SIDE_SIZE
TILE_SIZE_V = int(2 / np.sqrt(3) * TILE_SIZE)  # size of each tile in pixels, 2xTILE_SIDE_SIZE

# Tile positioning
TILE_SPACING = 0  # space between tiles in pixels (Horizontal)
TILE_VSPACING = int(TILE_SIZE *0.15) # space between tiles in pixels (Vertical)
TILES_OFFSET_H = CANVAS_WIDTH/2 - 2.5 * TILE_SIZE
TILES_OFFSET_V = CANVAS_HEIGHT/2 - int(2 * TILE_SIZE_V)
ROW_NUM_TILES = [3, 4, 5, 4, 3]  # number of tiles in each row from top to bottom
ROW_START_COLUMNS = [2, 1, 0, 1, 2]  # starting column number for each row

# Background properties
#BACKGROUND_SIZE_H = int(265*6.4)   # size of Background Tiles
BKG_NUDGE_H = 0.04
BKG_NUDGE_V = 0.01
BACKGROUND_OFFSET_H = 0
BACKGROUND_OFFSET_V = - 5 
BACKGROUND_SIZE_H = int( (5 + 5 * np.sqrt(3) / 6 )* TILE_SIZE * (1 + BKG_NUDGE_H))   # size of Background Tiles
BACKGROUND_SIZE_V =  int(5 * TILE_SIZE_V  * (1+BKG_NUDGE_V))   # size of Background Tiles

# Ship properties
SHIP_NUDGE = 1.4
SHIP_SIZE_H = int(BACKGROUND_SIZE_H * 25 / 265 / 2 * SHIP_NUDGE)
SHIP_SIZE_V = int(BACKGROUND_SIZE_H * 29 / 265 / 2 * SHIP_NUDGE)
SHIP_TO_BKG_RATIO = 40/46 # Compared to background, how far are the ships around the center?

NUMBER_SIZE = int( TILE_SIZE * 0.4 )
#}}}

# Arrays necessary for function of the code {{{
TILE_ASSETS = {
    "desert": "./assets/images/desert.png",
    "brick": "./assets/images/brick.png",
    "lumber": "./assets/images/lumber.png",
    "ore": "./assets/images/ore.png",
    "sheep": "./assets/images/sheep.png",
    "wheat": "./assets/images/wheat.png"
}

NUMBER_ASSETS = {
    2: "./assets/images/2.png",
    3: "./assets/images/3.png",
    4: "./assets/images/4.png",
    5: "./assets/images/5.png",
    6: "./assets/images/6.png",
    8: "./assets/images/8.png",
    9: "./assets/images/9.png",
    10: "./assets/images/10.png",
    11: "./assets/images/11.png",
    12: "./assets/images/12.png",
}


SHIP_ASSETS = {
    "31": "./assets/images/ships/31.png",
    "wheat": "./assets/images/ships/wheat.png",
    "ore": "./assets/images/ships/ore.png",
    "lumber": "./assets/images/ships/lumber.png",
    "brick": "./assets/images/ships/brick.png",
    "sheep": "./assets/images/ships/sheep.png"
}

#0.1 corresponds to ~6 mm
SHIP_LOCATION = [(1.0 - 0.1, 0.0),
 (0.766044443118978, 0.6427876096865393),
 (0.17364817766693041, 0.984807753012208),
 (-0.4999999999999998, 0.8660254037844387),
 (-0.9396926207859083, 0.3420201433256689),
 (-0.9396926207859084, -0.34202014332566866),
 (-0.5000000000000004, -0.8660254037844384),
 (0.17364817766692997, -0.9848077530122081),
 (0.7660444431189778, -0.6427876096865396)]

SHIP_INFO = [
(1,3),
(2,2),
(2,4),
(3,3),
(4,2),
(4,4),
(5,3),
(6,2),
(6,4),
]

vertices = [
        (CANVAS_WIDTH / 2 - BACKGROUND_SIZE_H / 4, CANVAS_HEIGHT / 2 + BACKGROUND_SIZE_V / 2),  # Bottom-left point
        (CANVAS_WIDTH / 2 + BACKGROUND_SIZE_H / 4, CANVAS_HEIGHT / 2 + BACKGROUND_SIZE_V / 2),  # Bottom-right point
        (CANVAS_WIDTH / 2 + BACKGROUND_SIZE_H / 2, CANVAS_HEIGHT / 2),  # Right point
        (CANVAS_WIDTH / 2 + BACKGROUND_SIZE_H / 4, CANVAS_HEIGHT / 2 - BACKGROUND_SIZE_V / 2),  # Top-right point
        (CANVAS_WIDTH / 2 - BACKGROUND_SIZE_H / 4, CANVAS_HEIGHT / 2 - BACKGROUND_SIZE_V / 2),  # Top-left point
        (CANVAS_WIDTH / 2 - BACKGROUND_SIZE_H / 2, CANVAS_HEIGHT / 2),  # Left point
]

SHIP_ANGLES = [60, 60, 0, -45, -60, -120, 180,  180, 120]

#}}}

# Defining Classes {{{

class Tile:
    def __init__(self, tile_type, number):
        self.tile_type = tile_type
        self.number = number
        self.image_path = TILE_ASSETS[tile_type]
"""
class Ship:
    def __init__(self, ship_type):
        self.ship_type = ship_type
        self.image_path = SHIP_ASSETS[ship_type]
"""
class Ship:
    def __init__(self, type):
        self.type = type


class Game:
    def __init__(self, pieces, ships, locs=None):
        self.pieces = pieces
        self.ships = ships
        self.locs = locs if locs else []
#}}}


# Helper functions {{{
# Function to shuffle the elements of the list
def shuffle(list_: List) -> List:
    random.shuffle(list_)
    return list_

# Function to pop a random element from the list
def pop_random(list_: List) -> any:
    return list_.pop(random.randrange(len(list_)))
#}}}

# Unused moves-defining arrays {{{
all_pieces = ["desert","brick","brick","brick","lumber","lumber","lumber","lumber","ore","ore","ore","sheep","sheep","sheep","sheep","wheat","wheat","wheat","wheat"]
all_probs = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
all_ships = ["31", "31", "31", "31", "wheat", "ore", "lumber", "brick", "sheep"]

moves = ['Red', 'Blue', 'Yellow', 'White', 'White', 'Yellow', 'Blue', 'Red']
alt_moves = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
alt_order = [0, 3, 7, 12, 16, 17, 18, 15, 11, 6, 2, 1, 4, 8, 13, 14, 10, 5, 9]

adjacent = {
  0: [1, 3, 4],
  1: [0, 2, 4, 5],
  2: [1, 5, 6],
  3: [0, 4, 7, 8],
  4: [0, 1, 3, 5, 8, 9],
  5: [1, 2, 4, 6, 9, 10],
  6: [2, 5, 10, 11],
  7: [3, 8, 12],
  8: [3, 4, 7, 9, 12, 13],
  9: [4, 5, 8, 10, 13, 14],
  10: [5, 6, 9, 11, 14, 15],
  11: [6, 10, 15],
  12: [7, 8, 13, 16],
  13: [8, 9, 12, 14, 16, 17],
  14: [9, 10, 13, 15, 17, 18],
  15: [10, 11, 14, 18],
  16: [12, 13, 17],
  17: [13, 14, 16, 18],
  18: [14, 15, 17],
}
#}}}

# New game types {{{
def new_spiral_game():
    board = shuffle(all_pieces)
    probs = shuffle(all_probs)
    ships = shuffle(all_ships)

    pieces = []
    for i in range(len(board)):
        pieces.append(Tile(board[i], 7))

    # Add in the numbers
    alt_index = 0
    for i in range(len(alt_order)):
        if pieces[alt_order[i]].tile_type != "desert":  # Use tile_type instead of resource
            pieces[alt_order[i]].number = alt_moves[alt_index]
            alt_index += 1

    these_ships = []
    for i in range(len(ships)):
        these_ships.append(Ship(ships[i]))

    return Game(pieces, these_ships)


# This is the newPseudoRandomGame function
def new_pseudo_random_game():
    board = shuffle(all_pieces.copy())
    probs = shuffle([p for p in all_probs if p not in [6, 8]])
    ships = shuffle(all_ships.copy())

    possibilities = []

    # Put in all of the tiles
    pieces = []
    for i in range(len(board)):
        pieces.append(Tile(board[i], 7))
        if board[i] != "desert":
            possibilities.append(i)

    # Place the 6's and 8's
    to_place = [6, 6, 8, 8]
    for i in range(len(to_place)):
        pos = pop_random(possibilities)
        pieces[pos].number = to_place[i]
        possibilities = [e for e in possibilities if e not in adjacent[pos]]

    # Place the rest of them
    for i in range(len(board)):
        if board[i] != "desert" and pieces[i].number == 7:
            pieces[i].number = probs.pop()

    these_ships = []
    for i in range(len(ships)):
        these_ships.append(Ship(ships[i]))

    return Game(pieces, these_ships)

# This is the newRandomGame function
def new_random_game():
    board = shuffle(all_pieces.copy())
    probs = shuffle(all_probs.copy())
    ships = shuffle(all_ships.copy())

    pieces = []
    for i in range(len(board)):
        if board[i] == "desert":
            pieces.append(Tile(board[i], 7))
        else:
            pieces.append(Tile(board[i], probs.pop()))

    these_ships = []
    for i in range(len(ships)):
        these_ships.append(Ship(ships[i]))

    return Game(pieces, these_ships)
#}}}


def draw_tile(draw, canvas, tile, position): #{{{
    # Open the tile image file
    tile_image = Image.open(tile.image_path)

    # Resize the image to fit the tile size
    tile_image = tile_image.resize((TILE_SIZE, int( 2 / np.sqrt(3) * TILE_SIZE)), Image.LANCZOS)

    # Convert the image to RGBA if it doesn't have an alpha channel
    if tile_image.mode != 'RGBA':
        tile_image = tile_image.convert('RGBA')

    # Extract the mask from the tile image
    mask = tile_image.split()[3]  # The alpha band is the 4th band in RGBA

    # Paste the tile image onto the canvas at the given position
    canvas.paste(tile_image, position, mask=mask)

    # If the tile type is not desert, draw the number
    if tile.tile_type != "desert":
        # Open the number image file
        number_image = Image.open(NUMBER_ASSETS[tile.number])

        # Convert the number image to RGBA if it doesn't have an alpha channel
        if number_image.mode != 'RGBA':
            number_image = number_image.convert('RGBA')

        # Resize the number image to be smaller than the tile size
        number_image = number_image.resize((NUMBER_SIZE, NUMBER_SIZE), Image.LANCZOS)

        # Calculate the position of the number to be in the center of the tile
        number_position = (position[0] + TILE_SIZE//2 - NUMBER_SIZE//2, position[1] + TILE_SIZE//2 - NUMBER_SIZE//2)

        # Extract the mask from the number image
        mask = number_image.split()[3]

        # Paste the number image onto the canvas at the given position
        canvas.paste(number_image, number_position, mask=mask)
#}}}

def draw_background(draw, canvas): #{{{
    # Open the tile image file
    tile_image = Image.open(background_image_path)

    # Resize the image to fit the tile size
    tile_image = tile_image.resize((BACKGROUND_SIZE_H, int( BACKGROUND_SIZE_V)), Image.LANCZOS)

    # Convert the image to RGBA if it doesn't have an alpha channel
    if tile_image.mode != 'RGBA':
        tile_image = tile_image.convert('RGBA')

    # Extract the mask from the tile image
    mask = tile_image.split()[3]  # The alpha band is the 4th band in RGBA
    position = (int(CANVAS_WIDTH/2 - BACKGROUND_SIZE_H/2 + BACKGROUND_OFFSET_H), int(CANVAS_HEIGHT/2- BACKGROUND_SIZE_V/2 + BACKGROUND_OFFSET_V))

    # Paste the tile image onto the canvas at the given position
    canvas.paste(tile_image, position, mask=mask)
#}}}

def calculate_position(index): #{{{
    row = 0
    while index >= ROW_NUM_TILES[row]:
        index -= ROW_NUM_TILES[row]
        row += 1
    column = ROW_START_COLUMNS[row] + index
    x = TILES_OFFSET_H + (TILE_SIZE + TILE_SPACING) * column - abs(row-2)*TILE_SIZE / 2
    y = TILES_OFFSET_V + (TILE_SIZE - TILE_VSPACING) * row
    return (round(x), round(y))
#}}}

def calculate_ship_position(index, total_ships): #{{{
    radius = BACKGROUND_SIZE_H * SHIP_TO_BKG_RATIO // 2  # ships are positioned on a circle with this radius
    #(x,y) = hexagon_intersection(radius, angle)
    (x,y) = SHIP_LOCATION[index]
    x = radius*x + CANVAS_WIDTH * 0.49
    y = radius*y + CANVAS_HEIGHT * 0.49
    return (round(x), round(y))  # round the values to nearest integers
#}}}

def find_ship_pivot(ship_info, max_point_id, vertices): #{{{
    side_num, point_id = ship_info
    # side_num: 0 - bottom side; 1 - right bottom side, etc.
    vertex_point = vertices[(side_num - 1) % 6 ]
    next_vertex_point = vertices[(side_num) % 6] # get the next vertex point. Reset to the starting one in case we went over the max vertex point
    x1, y1 = vertex_point
    x2, y2 = next_vertex_point
    side_length = np.sqrt( (x1-x2)**2 + (y1-y2)**2 ) # get the length of the bkg side
    angle = np.pi / 3 * (side_num - 1) # angle of the ship (with respect to the vertical)

    # length of the displacement of the pivot point from the vertex along the line
    if point_id ==1:
        lengthwise_d = TILE_SIZE_V / np.sqrt(3) / 2
    elif point_id == max_point_id:
        lengthwise_d = TILE_SIZE_V * np.sqrt(3) / 2 + TILE_SIZE * (max_point_id - 2) 
    else:
        lengthwise_d = TILE_SIZE_V / np.sqrt(3) + TILE_SIZE * (point_id - 3 / 2) 
    # obtain coordinates of displacement of pivot point from the vertex
    dx = lengthwise_d * np.cos(angle)
    dy = - lengthwise_d * np.sin(angle)
    x_pivot = x1 + dx
    y_pivot = y1 + dy

    return x_pivot, y_pivot, angle
#}}}

def draw_ship_V2(draw, canvas, ship, ship_info, max_point_id, vertices): #{{{

    x_pivot, y_pivot, angle = find_ship_pivot(ship_info, max_point_id, vertices)
    side_num, point_id = ship_info
    if side_num in [1]:
        dL = SHIP_SIZE_V * 0.7
        dx = -  dL * np.sin(angle)
        dy = - dL * np.cos(angle)
    elif side_num in [2]:
        dL = SHIP_SIZE_V 
        dx = -  dL * np.sin(angle) + SHIP_SIZE_H * np.cos(angle) * 0.4 
        dy = - dL * np.cos(angle)  - SHIP_SIZE_H * np.sin(angle)  * 0.4 
    elif side_num in [3]:
        dL = SHIP_SIZE_V * 0.7
        dx = -  dL * np.sin(angle)+ SHIP_SIZE_H * np.cos(angle) * 0.2 
        dy = - dL * np.cos(angle) - SHIP_SIZE_H * np.sin(angle) * 0.2 
    elif side_num in [4]:
        dL = SHIP_SIZE_V * 0.6 
        dx = -  dL * np.sin(angle) + SHIP_SIZE_H * np.cos(angle) * 0.3 
        dy = - dL * np.cos(angle) - SHIP_SIZE_H * np.sin(angle)  * 0.3
    elif side_num in [5]:
        dL = SHIP_SIZE_V * 0.3 
        dx = -  dL * np.sin(angle) - SHIP_SIZE_H * np.cos(angle) * 0.2 
        dy = - dL * np.cos(angle)  + SHIP_SIZE_H * np.sin(angle) * 0.2
    else:
        dL = SHIP_SIZE_V / 2
        dx = -  dL * np.sin(angle)
        dy = - dL * np.cos(angle)
    position = (round(x_pivot + dx - SHIP_SIZE_H/2), round(y_pivot + dy - SHIP_SIZE_V/2))

    # Open the ship image file
    ship_image = Image.open(SHIP_ASSETS[ship.type])

    # Resize the image to fit the ship size
    ship_image = ship_image.resize((SHIP_SIZE_H, SHIP_SIZE_V), Image.LANCZOS)

    # Convert the image to RGBA if it doesn't have an alpha channel
    ship_image = ship_image.convert('RGBA')
    
    # Rotate the image
    ship_image = ship_image.rotate(angle * 180 / np.pi, resample=Image.BICUBIC, expand=True)

    # Extract the mask from the ship image
    mask = ship_image.split()[3]  # The alpha band is the 4th band in RGBA

    # Paste the ship image onto the canvas at the given position
    canvas.paste(ship_image, position, mask=mask)
#}}}

def draw_hexagon(draw, canvas, size_h, size_v, color="#DCC894"): #{{{
    # Calculate the points of the hexagon
    points = [
        (canvas.width / 2 - size_h / 2, canvas.height / 2),  # Left point
        (canvas.width / 2 - size_h / 4, canvas.height / 2 - size_v / 2),  # Top-left point
        (canvas.width / 2 + size_h / 4, canvas.height / 2 - size_v / 2),  # Top-right point
        (canvas.width / 2 + size_h / 2, canvas.height / 2),  # Right point
        (canvas.width / 2 + size_h / 4, canvas.height / 2 + size_v / 2),  # Bottom-right point
        (canvas.width / 2 - size_h / 4, canvas.height / 2 + size_v / 2),  # Bottom-left point
    ]

    # Draw the hexagon
    draw.polygon(points, fill=color)
#}}}

def draw_empty_hexagon(draw, canvas, size_h, size_v, color="#FF0000"): #{{{
    # Calculate the points of the hexagon
    """
    points = [
        (canvas.width / 2 - size_h / 2, canvas.height / 2),  # Left point
        (canvas.width / 2 - size_h / 4, canvas.height / 2 - size_v / 2),  # Top-left point
        (canvas.width / 2 + size_h / 4, canvas.height / 2 - size_v / 2),  # Top-right point
        (canvas.width / 2 + size_h / 2, canvas.height / 2),  # Right point
        (canvas.width / 2 + size_h / 4, canvas.height / 2 + size_v / 2),  # Bottom-right point
        (canvas.width / 2 - size_h / 4, canvas.height / 2 + size_v / 2),  # Bottom-left point
    ]
    """
    points = vertices

    # Draw the hexagon
    draw.polygon(points, fill=None)
#}}}

def draw_game(game): #{{{
    # Create a blank canvas
    canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), 'black')
    
    # Create a drawing object
    draw = ImageDraw.Draw(canvas)
    
    draw_hexagon(draw, canvas, BACKGROUND_SIZE_H*0.9, BACKGROUND_SIZE_V*0.9)
    
    draw_background(draw, canvas)

    #draw_empty_hexagon(draw, canvas, BACKGROUND_SIZE_H, BACKGROUND_SIZE_V)

    # Draw each tile at the correct position
    for index in range(len(game.pieces)):
        tile = game.pieces[index]
        position = calculate_position(index)
        draw_tile(draw, canvas, tile, position)
    
    total_ships = len(game.ships)

    #draw_empty_hexagon(draw, canvas, BACKGROUND_SIZE_H, BACKGROUND_SIZE_V)
    
    # Draw each ship at the correct position
    for index in range(total_ships):
        ship = game.ships[index]
        draw_ship_V2(draw, canvas, ship, SHIP_INFO[index], 4, vertices)
    
    # Save the image to a file
    canvas.save(output_name)
    print(f'The map was saved in {output_name}!')
#}}}

