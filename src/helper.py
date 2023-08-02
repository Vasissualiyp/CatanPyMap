import base64
import random

# Shuffle function
def shuffle(array):
    random.shuffle(array)
    return array

# Binary to Base64
def encode64(binary):
    return base64.b64encode(int(binary, 2).to_bytes((len(binary) + 7) // 8, byteorder='big')).decode()

# Base64 to binary
def decode64(base64_string):
    return "{0:b}".format(int.from_bytes(base64.b64decode(base64_string), byteorder='big'))

tile_types = ["desert", "brick", "lumber", "ore", "sheep", "wheat"]
ship_types = ["31", "wheat", "ore", "lumber", "brick", "sheep"]


# Encodes a game into a base64 string
def encode(game):
    binary = ""
    if len(game.pieces) == 19 and len(game.ships) == 9:
        for i in range(len(game.pieces)):
            binary += game.pieces[i].binary()
        for i in range(len(game.ships)):
            binary += game.ships[i].binary()
    return encode64(binary)

def encode_moves(game):
    binary = ""
    for i in range(8):
        if i < len(game.locs):
            num_string = "{0:b}".format(game.locs[i])
        else:
            num_string = "111111"
        binary += ("000000" + num_string)[-6:]
    return encode64(binary)

# Decodes a base64 string into a game
def decode(base64_string):
    binary = decode64(base64_string)
    binary = binary[-(19 * 7 + 3 * 9):]

    pieces = []
    ships = []
    if len(binary) == 19 * 7 + 3 * 9:
        for i in range(19):
            slice_ = binary[i*7:(i+1)*7]
            type_ = tile_types[int(slice_[:3], 2)]
            num = int(slice_[3:], 2)
            pieces.append(Tile(type_, num))
        for i in range(9):
            slice_ = binary[19*7 + i*3:19*7 + (i+1)*3]
            type_ = ship_types[int(slice_, 2)]
            ships.append(Ship(type_))
    return Game(pieces, ships)

# Decodes a base64 string into moves
def decode_moves(base64_string):
    binary = decode64(base64_string)
    binary = binary[-(6 * 8):]

    locs = []
    if len(binary) == 6 * 8:
        for i in range(8):
            slice_ = binary[i*6:(i+1)*6]
            num = int(slice_, 2)
            if num != 63:
                locs.append(num)
    return locs

