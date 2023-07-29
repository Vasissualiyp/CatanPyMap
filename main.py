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

def define_vars(monitor_info, params):
    # Final image size
    params.canvas_width, params.canvas_height = monitor_info
    #params.canvas_width = 3840
    #params.canvas_height = 2160

    # Tile properties
    params.tile_size = int(40*6.4)  # size of each tile in pixels, 2xTILE_SIDE_SIZE
    params.tile_size_v = int(2 / np.sqrt(3) * params.tile_size)  # size of each tile in pixels, 2xTILE_SIDE_SIZE

    # Tile positioning
    params.tile_spacing = 0  # space between tiles in pixels (Horizontal)
    params.tile_vspacing = int(params.tile_size *0.15) # space between tiles in pixels (Vertical)
    params.tiles_offset_h = params.canvas_width/2 - 2.5 * params.tile_size
    params.tiles_offset_v = params.canvas_height/2 - int(2 * params.tile_size_v)
    params.row_num_tiles = [3, 4, 5, 4, 3]  # number of tiles in each row from top to bottom
    params.row_start_columns = [2, 1, 0, 1, 2]  # starting column number for each row

    # Background properties
    #params.background_size_h = int(265*6.4)   # size of Background Tiles
    params.bkg_nudge_h = 0.04
    params.bkg_nudge_v = 0.01
    params.background_offset_h = 0
    params.background_offset_v = - 5 
    params.background_size_h = int( (5 + 5 * np.sqrt(3) / 6 )* params.tile_size * (1 + params.bkg_nudge_h))   # size of Background Tiles
    params.background_size_v =  int(5 * params.tile_size_v  * (1+params.bkg_nudge_v))   # size of Background Tiles

    # Ship properties
    params.ship_nudge = 1.4
    params.ship_size_h = int(params.background_size_h * 25 / 265 / 2 * params.ship_nudge)
    params.ship_size_v = int(params.background_size_h * 29 / 265 / 2 * params.ship_nudge)
    params.ship_to_bkg_ratio = 40/46 # Compared to background, how far are the ships around the center?

    params.number_size = int( params.tile_size * 0.4 )
    #}}}

class Parameters: #{{{
    def __init__(self, monitor_res):
        self.canvas_width, self.canvas_height, self.lineardim_x, self.lineardim_y = monitor_res
        px_per_mm = (self.canvas_width/self.lineardim_x + self.canvas_height /self.lineardim_y) / 2
        self.tile_size = int(40*2*3.2)
        self.tile_size_v = int(2 / np.sqrt(3) * self.tile_size)
        self.tile_spacing = 0
        self.tile_vspacing = int(self.tile_size *0.15)
        self.tiles_offset_h = self.canvas_width/2 - 2.5 * self.tile_size
        self.tiles_offset_v = self.canvas_height/2 - int(2 * self.tile_size_v)
        self.row_num_tiles = [3, 4, 5, 4, 3]
        self.row_start_columns = [2, 1, 0, 1, 2]
        self.bkg_nudge_h = 0.04
        self.bkg_nudge_v = 0.01
        self.background_offset_h = 0
        self.background_offset_v = - 5
        self.background_size_h = int( (5 + 5 * np.sqrt(3) / 6 )* self.tile_size * (1 + self.bkg_nudge_h))
        self.background_size_v =  int(5 * self.tile_size_v  * (1+self.bkg_nudge_v))
        self.ship_nudge = 1.4
        self.ship_size_h = int(self.background_size_h * 25 / 265 / 2 * self.ship_nudge)
        self.ship_size_v = int(self.background_size_h * 29 / 265 / 2 * self.ship_nudge)
        self.ship_to_bkg_ratio = 40/46
        self.number_size = int( self.tile_size * 0.4 )
        self.tile_assets = {
            "desert": "./assets/images/desert.png",
            "brick": "./assets/images/brick.png",
            "lumber": "./assets/images/lumber.png",
            "ore": "./assets/images/ore.png",
            "sheep": "./assets/images/sheep.png",
            "wheat": "./assets/images/wheat.png"
        }

        self.number_assets = {
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


        self.ship_assets = {
            "31": "./assets/images/ships/31.png",
            "wheat": "./assets/images/ships/wheat.png",
            "ore": "./assets/images/ships/ore.png",
            "lumber": "./assets/images/ships/lumber.png",
            "brick": "./assets/images/ships/brick.png",
            "sheep": "./assets/images/ships/sheep.png"
        }

        #0.1 corresponds to ~6 mm
        self.ship_location = [(1.0 - 0.1, 0.0),
         (0.766044443118978, 0.6427876096865393),
         (0.17364817766693041, 0.984807753012208),
         (-0.4999999999999998, 0.8660254037844387),
         (-0.9396926207859083, 0.3420201433256689),
         (-0.9396926207859084, -0.34202014332566866),
         (-0.5000000000000004, -0.8660254037844384),
         (0.17364817766692997, -0.9848077530122081),
         (0.7660444431189778, -0.6427876096865396)]

        self.ship_info = [
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

        self.vertices = [
                (self.canvas_width / 2 - self.background_size_h / 4, self.canvas_height / 2 + self.background_size_v / 2),  # Bottom-left point
                (self.canvas_width / 2 + self.background_size_h / 4, self.canvas_height / 2 + self.background_size_v / 2),  # Bottom-right point
                (self.canvas_width / 2 + self.background_size_h / 2, self.canvas_height / 2),  # Right point
                (self.canvas_width / 2 + self.background_size_h / 4, self.canvas_height / 2 - self.background_size_v / 2),  # Top-right point
                (self.canvas_width / 2 - self.background_size_h / 4, self.canvas_height / 2 - self.background_size_v / 2),  # Top-left point
                (self.canvas_width / 2 - self.background_size_h / 2, self.canvas_height / 2),  # Left point
        ]

#}}}

# Defining Classes {{{

class Tile:
    def __init__(self, tile_type, number, params):
        self.tile_type = tile_type
        self.number = number
        self.image_path = params.tile_assets[tile_type]
"""
class Ship:
    def __init__(self, ship_type):
        self.ship_type = ship_type
        self.image_path = params.ship_assets[ship_type]
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
def new_spiral_game(monitor_info, params):
    board = shuffle(all_pieces)
    probs = shuffle(all_probs)
    ships = shuffle(all_ships)

    pieces = []
    for i in range(len(board)):
        pieces.append(Tile(board[i], 7, params))

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
def new_pseudo_random_game(monitor_info, params):
    board = shuffle(all_pieces.copy())
    probs = shuffle([p for p in all_probs if p not in [6, 8]])
    ships = shuffle(all_ships.copy())

    possibilities = []

    # Put in all of the tiles
    pieces = []
    for i in range(len(board)):
        pieces.append(Tile(board[i], 7, params))
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
def new_random_game(monitor_info, params):
    board = shuffle(all_pieces.copy())
    probs = shuffle(all_probs.copy())
    ships = shuffle(all_ships.copy())

    pieces = []
    for i in range(len(board)):
        if board[i] == "desert":
            pieces.append(Tile(board[i], 7, params))
        else:
            pieces.append(Tile(board[i], probs.pop()))

    these_ships = []
    for i in range(len(ships)):
        these_ships.append(Ship(ships[i]))

    return Game(pieces, these_ships)
#}}}


def draw_tile(draw, canvas, tile, position, params): #{{{
    # Open the tile image file
    tile_image = Image.open(tile.image_path)

    # Resize the image to fit the tile size
    tile_image = tile_image.resize((params.tile_size, int( 2 / np.sqrt(3) * params.tile_size)), Image.LANCZOS)

    # Convert the image to RGBa if it doesn't have an alpha channel
    if tile_image.mode != 'RGBA':
        tile_image = tile_image.convert('RGBA')

    # Extract the mask from the tile image
    mask = tile_image.split()[3]  # The alpha band is the 4th band in RGBa

    # Paste the tile image onto the canvas at the given position
    canvas.paste(tile_image, position, mask=mask)

    # If the tile type is not desert, draw the number
    if tile.tile_type != "desert":
        # Open the number image file
        number_image = Image.open(params.number_assets[tile.number])

        # Convert the number image to RGBa if it doesn't have an alpha channel
        if number_image.mode != 'RGBA':
            number_image = number_image.convert('RGBA')

        # Resize the number image to be smaller than the tile size
        number_image = number_image.resize((params.number_size, params.number_size), Image.LANCZOS)

        # Calculate the position of the number to be in the center of the tile
        number_position = (position[0] + params.tile_size//2 - params.number_size//2, position[1] + params.tile_size//2 - params.number_size//2)

        # Extract the mask from the number image
        mask = number_image.split()[3]

        # Paste the number image onto the canvas at the given position
        canvas.paste(number_image, number_position, mask=mask)
#}}}

def draw_background(draw, canvas, params): #{{{
    # Open the tile image file
    tile_image = Image.open(background_image_path)

    # Resize the image to fit the tile size
    tile_image = tile_image.resize((params.background_size_h, int( params.background_size_v)), Image.LANCZOS)

    # Convert the image to RGBa if it doesn't have an alpha channel
    if tile_image.mode != 'RGBA':
        tile_image = tile_image.convert('RGBA')

    # Extract the mask from the tile image
    mask = tile_image.split()[3]  # The alpha band is the 4th band in RGBa
    position = (int(params.canvas_width/2 - params.background_size_h/2 + params.background_offset_h), int(params.canvas_height/2- params.background_size_v/2 + params.background_offset_v))

    # Paste the tile image onto the canvas at the given position
    canvas.paste(tile_image, position, mask=mask)
#}}}

def calculate_position(index, params): #{{{
    row = 0
    while index >= params.row_num_tiles[row]:
        index -= params.row_num_tiles[row]
        row += 1
    column = params.row_start_columns[row] + index
    x = params.tiles_offset_h + (params.tile_size + params.tile_spacing) * column - abs(row-2)*params.tile_size / 2
    y = params.tiles_offset_v + (params.tile_size - params.tile_vspacing) * row
    return (round(x), round(y))
#}}}

def calculate_ship_position(index, total_ships, params): #{{{
    radius = params.background_size_h * params.ship_to_bkg_ratio // 2  # ships are positioned on a circle with this radius
    #(x,y) = hexagon_intersection(radius, angle)
    (x,y) = params.ship_location[index]
    x = radius*x + params.canvas_width * 0.49
    y = radius*y + params.canvas_height * 0.49
    return (round(x), round(y))  # round the values to nearest integers
#}}}

def find_ship_pivot(ship_info, max_point_id, params): #{{{
    side_num, point_id = ship_info
    # side_num: 0 - bottom side; 1 - right bottom side, etc.
    vertex_point = params.vertices[(side_num - 1) % 6 ]
    next_vertex_point = params.vertices[(side_num) % 6] # get the next vertex point. Reset to the starting one in case we went over the max vertex point
    x1, y1 = vertex_point
    x2, y2 = next_vertex_point
    side_length = np.sqrt( (x1-x2)**2 + (y1-y2)**2 ) # get the length of the bkg side
    angle = np.pi / 3 * (side_num - 1) # angle of the ship (with respect to the vertical)

    # length of the displacement of the pivot point from the vertex along the line
    if point_id ==1:
        lengthwise_d = params.tile_size_v / np.sqrt(3) / 2
    elif point_id == max_point_id:
        lengthwise_d = params.tile_size_v * np.sqrt(3) / 2 + params.tile_size * (max_point_id - 2) 
    else:
        lengthwise_d = params.tile_size_v / np.sqrt(3) + params.tile_size * (point_id - 3 / 2) 
    # obtain coordinates of displacement of pivot point from the vertex
    dx = lengthwise_d * np.cos(angle)
    dy = - lengthwise_d * np.sin(angle)
    x_pivot = x1 + dx
    y_pivot = y1 + dy

    return x_pivot, y_pivot, angle
#}}}

def draw_ship_V2(draw, canvas, ship, ship_info, max_point_id, params): #{{{

    x_pivot, y_pivot, angle = find_ship_pivot(ship_info, max_point_id, params)
    side_num, point_id = ship_info
    if side_num in [1]:
        dL = params.ship_size_v * 0.7
        dx = -  dL * np.sin(angle)
        dy = - dL * np.cos(angle)
    elif side_num in [2]:
        dL = params.ship_size_v 
        dx = -  dL * np.sin(angle) + params.ship_size_h * np.cos(angle) * 0.4 
        dy = - dL * np.cos(angle)  - params.ship_size_h * np.sin(angle)  * 0.4 
    elif side_num in [3]:
        dL = params.ship_size_v * 0.7
        dx = -  dL * np.sin(angle)+ params.ship_size_h * np.cos(angle) * 0.2 
        dy = - dL * np.cos(angle) - params.ship_size_h * np.sin(angle) * 0.2 
    elif side_num in [4]:
        dL = params.ship_size_v * 0.6 
        dx = -  dL * np.sin(angle) + params.ship_size_h * np.cos(angle) * 0.3 
        dy = - dL * np.cos(angle) - params.ship_size_h * np.sin(angle)  * 0.3
    elif side_num in [5]:
        dL = params.ship_size_v * 0.3 
        dx = -  dL * np.sin(angle) - params.ship_size_h * np.cos(angle) * 0.2 
        dy = - dL * np.cos(angle)  + params.ship_size_h * np.sin(angle) * 0.2
    else:
        dL = params.ship_size_v / 2
        dx = -  dL * np.sin(angle)
        dy = - dL * np.cos(angle)
    position = (round(x_pivot + dx - params.ship_size_h/2), round(y_pivot + dy - params.ship_size_v/2))

    # Open the ship image file
    ship_image = Image.open(params.ship_assets[ship.type])

    # Resize the image to fit the ship size
    ship_image = ship_image.resize((params.ship_size_h, params.ship_size_v), Image.LANCZOS)

    # Convert the image to RGBa if it doesn't have an alpha channel
    ship_image = ship_image.convert('RGBa')
    
    # Rotate the image
    ship_image = ship_image.rotate(angle * 180 / np.pi, resample=Image.BICUBIC, expand=True)

    # Extract the mask from the ship image
    mask = ship_image.split()[3]  # The alpha band is the 4th band in RGBa

    # Paste the ship image onto the canvas at the given position
    canvas.paste(ship_image, position, mask=mask)
#}}}

def draw_hexagon(draw, canvas, size_h, size_v, params, color="#DCC894"): #{{{
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

def draw_empty_hexagon(draw, canvas, size_h, size_v, params, color="#FF0000"): #{{{
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
    points = params.vertices

    # Draw the hexagon
    draw.polygon(points, fill=None)
#}}}

def draw_game(game, params): #{{{
    # Create a blank canvas
    canvas = Image.new('RGB', (params.canvas_width, params.canvas_height), 'black')
    
    # Create a drawing object
    draw = ImageDraw.Draw(canvas)
    
    draw_hexagon(draw, canvas, params.background_size_h*0.9, params.background_size_v*0.9, params)
    
    draw_background(draw, canvas, params)

    #draw_empty_hexagon(draw, canvas, params.background_size_h, params.background_size_v)

    # Draw each tile at the correct position
    for index in range(len(game.pieces)):
        tile = game.pieces[index]
        position = calculate_position(index, params)
        draw_tile(draw, canvas, tile, position, params)
    
    total_ships = len(game.ships)

    #draw_empty_hexagon(draw, canvas, params.background_size_h, params.background_size_v, params)
    
    # Draw each ship at the correct position
    for index in range(total_ships):
        ship = game.ships[index]
        draw_ship_V2(draw, canvas, ship, params.ship_info[index], 4, params)
    
    # Save the image to a file
    canvas.save(output_name)
    print(f'The map was saved in {output_name}!')
#}}}

