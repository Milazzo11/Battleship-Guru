"""
Battleship Probability Mapper.

:author: Max Milazzo
"""


import os
import random
import pickle
import numpy as np


MODE = "n"
# mode "t" allows for ships to touch and mode "n" does not


GRID = (10, 10)
# Battleship is typically played on a 10x10 grid


LOGGING = True
# enable data log


DATA_DIR = "data"
# game data file storage directory


ASCII_START_CHAR = 65
# ASCII start character


class Battleship:
    """
    Battship game object.
    """
    
    def __init__(self, ships: list, mode: str, width: int, height: int) -> None:
        """
        Battship game object definition.
        
        :param ships: list of ship sizes in game
        :param mode: game mode being played
        :param width: game board width
        :param height: game board height
        """
        
        self.ships = ships
        self.mode = mode
        self.width = width
        self.height = height
        # set passed data values
        
        self.board = []
        self.hit_mem = []
        
        for x in range(self.width):
            self.board.append([])
        
            for y in range(self.height):
                self.board[x].append(".")
                # initialize board values to empty
        
    
    def _gen_prob_map(self) -> None:
        """
        Generate updated game board probability map.
        """
        
        self.prob_map = np.zeros((self.width, self.height), dtype="int32")
        # initialize empty map
 
        for ship in self.ships:
        # loop through all ships still in game
        
            for y in range(self.height):
                for x in range(self.width):
                    x_valid = True
                    y_valid = True
                    # mark coordinates initaially as valid ship location
                    # (down and right)
                    
                    for shift in range(ship):
                        if x + shift >= self.width or self.board[x + shift][y] != ".":
                            x_valid = False
                            # ship location invalid from coordinates
                            # (going right)
                            
                        if y + shift >= self.height or self.board[x][y + shift] != ".":
                            y_valid = False
                            # ship location invalid from coordinates
                            # (going down)
                    
                    if x_valid:
                        for x_shift in range(ship):
                            self.prob_map[x + x_shift][y] += 1
                            # update probability map if right ship location is
                            # valid from coordinates
                            
                    if y_valid:
                        for y_shift in range(ship):
                            self.prob_map[x][y + y_shift] += 1
                            # update probability map if down ship location is
                            # valid from coordinates

    
    def _gen_hit_map(self, tile_x: int, tile_y: int) -> dict:
        """
        Generate "hit map" marking the best possible hit locations given a
        single set of coordinates.
        
        :param tile_x: tile x-coordinate
        :param tile_y: tile y-coordinate
        """
        
        right = 0
        left = 0
        down = 0
        up = 0
        # set direction hit "value" tracker values to zero
        
        for right_loc in range(tile_x + 1, self.width):
            if self.board[right_loc][tile_y] != ".":
                break
                
            right += 1
            # calculate right hit value
                
        for left_loc in reversed(range(0, tile_x)):
            if self.board[left_loc][tile_y] != ".":
                break
                
            left += 1
            # calculate left hit value
                
        for down_loc in range(tile_y + 1, self.height):
            if self.board[tile_x][down_loc] != ".":
                break
                
            down += 1
            # calculate down hit value
                
        for up_loc in reversed(range(0, tile_y)):
            if self.board[tile_x][up_loc] != ".":
                break
                
            up += 1
            # calculate up hit value
            
        return {
        
            (tile_x + 1, tile_y) : right,
            (tile_x - 1, tile_y) : left,
            (tile_x, tile_y + 1) : down,
            (tile_x, tile_y - 1) : up

        }
        # return compiled "hit map"

  
    def predict(self) -> None:
        """
        Generate a prediction for the next best possible move.
        """

        if len(self.hit_mem) == 0:
        # if no non-sinking hits registered
        
            self._gen_prob_map()
            # generate updated game board probability map
            
            if LOGGING:
                print("Probability map:\n")
                print(np.transpose(self.prob_map))
                print("\n")
                # log probability map

            pred = random.choice(
                np.argwhere(self.prob_map == np.max(self.prob_map))
            )
            # select a maximum hit prediction based on probability map

        else:
        # if one or more non-sinking hits is registered

            if len(self.hit_mem) == 1:
            # if only one hit is registered
            
                hit_map = self._gen_hit_map(
                    self.hit_mem[0][0], self.hit_mem[0][1]
                )
                # generate standard single-coordinates hit map
            
            elif self.hit_mem[0][0] == self.hit_mem[-1][0]:
            # current hits oriented in the "up-and-down" direction
                
                self.hit_mem.sort(key=lambda coord: coord[1])
                # sort hit memory list in sequential order

                lower_hit = self.hit_mem[-1]
                upper_hit = self.hit_mem[0]
                # mark current hit endpoints

                hit_map = {
                
                    (lower_hit[0], lower_hit[1] + 1) : self._gen_hit_map(
                        lower_hit[0], lower_hit[1]
                    )[(lower_hit[0], lower_hit[1] + 1)],
                    
                    (upper_hit[0], upper_hit[1] - 1) : self._gen_hit_map(
                        upper_hit[0], upper_hit[1]
                    )[(upper_hit[0], upper_hit[1] - 1)]

                }
                # generate "up-and-down" hit map for current orientation
        
            else:
            # current hits oriented in the "left-to-right" direction
            
                self.hit_mem.sort(key=lambda coord: coord[0])
                # sort hit memory list in sequential order
                
                left_hit = self.hit_mem[-1]
                right_hit = self.hit_mem[0]
                # mark current hit endpoints
                
                hit_map = {
                
                    (left_hit[0] + 1, left_hit[1]): self._gen_hit_map(
                        left_hit[0], left_hit[1]
                    )[(left_hit[0] + 1, left_hit[1])],
                    
                    (right_hit[0] - 1, right_hit[1]): self._gen_hit_map(
                        right_hit[0], right_hit[1]
                    )[(right_hit[0] - 1, right_hit[1])]

                }
                # generate "left-to-right" hit map for current orientation
            
            if LOGGING:
                print("Hit prediction map:\n")
                print(hit_map)
                print("\n")
                # log hit map
            
            dict_max = max(hit_map.values())
            # find the maximum value in the hit map dictionary

            pred_choices = [
                key for key, value in hit_map.items() if value == dict_max
            ]
            # find all hit map keys where the maximum value occurs
            
            pred = random.choice(pred_choices)
            # select a maximum hit prediction
            
        self.pred_x = pred[0]
        self.pred_y = pred[1]
        # set predictions
        
        self.board[self.pred_x][self.pred_y] = "+"
        # add prediction to game board
    

    def _clear_tile(self, tile_x: int, tile_y: int) -> None:
        """
        Sets a single non-ship tile to a miss.
        
        :param tile_x: tile x-coordinate
        :param tile_y: tile y-coordinate
        """
        
        if self.board[tile_x][tile_y] != "#":
            self.board[tile_x][tile_y] = "o"
    
    
    def _clear_edges(self, tile_x: int, tile_y: int) -> None:
        """
        Clears the edges of a sunk ship tile.
        
        :param tile_x: tile x-coordinate
        :param tile_y: tile y-coordinate
        """
        
        self._clear_tile(tile_x + 1, tile_y)
        self._clear_tile(tile_x - 1, tile_y)
        self._clear_tile(tile_x, tile_y + 1)
        self._clear_tile(tile_x, tile_y - 1)
        # clear horizontal and vertical edges
        
        self._clear_tile(tile_x + 1, tile_y + 1)
        self._clear_tile(tile_x - 1, tile_y - 1)
        self._clear_tile(tile_x + 1, tile_y - 1)
        self._clear_tile(tile_x - 1, tile_y + 1)
        # clear diagonal edges
    
    
    def sink(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """
        Registers a ship as sunk and updates game logic.
        
        :param start_x: starting ship tile x-coordinate
        :param start_y: starting ship tile y-coordinate
        :param end_x: ending ship tile x-coordinate
        :param end_y: ending ship tile y-coordinate
        
        :return: whether or not ship sink results in game ending
        """
        
        if start_x == end_x:
        # ship oriented in "up-and-down" direction
            
            if start_y > end_y:
                temp_y = start_y
                start_y = end_y
                end_y = temp_y
                # ensure start and end coordinate correctness

            sunk = end_y - start_y + 1
            # calculate sunk ship length
        
            while start_y <= end_y:
                self.board[start_x][start_y] = "#"
                self.hit_mem.remove((start_x, start_y))
                # register sunk tile
                
                if self.mode == "n":
                    self._clear_edges(start_x, start_y)
                    # mark sunk ship edges as "empty"
                    
                start_y += 1
                
        else:
        # ship oriented in "left-to-right" direction
        
            if start_x > end_x:
                temp_x = start_x
                start_x = end_x
                end_x = temp_x
                # ensure start and end coordinate correctness
        
            sunk = end_x - start_x + 1
            # calculate sunk ship length
        
            while start_x <= end_x:
                self.board[start_x][start_y] = "#"
                self.hit_mem.remove((start_x, start_y))
                # register sunk tile
                
                if self.mode == "n":
                    self._clear_edges(start_x, start_y)
                    # mark sunk ship edges as "empty"
                    
                start_x += 1
        
        for index in range(len(self.ships)):
            if self.ships[index] == sunk:
                del self.ships[index]
                break
                # remove ship from ship list
                # (and return "game over" = True if no more ships)
        
        if len(self.ships) == 0:
            return True
            
        return False
                
        
    def update(self, res: str) -> None:
        """
        Updates game board.
        
        :param res: move result string
        """
        
        self.board[self.pred_x][self.pred_y] = res
        # update game board
        
        if res == "x":
            self.hit_mem.append((self.pred_x, self.pred_y))
            # update hit memory list if needed

     
    def show(self) -> None:
        """
        Displays game board in command window.
        """
        
        print(end="  ")
        
        for count in range(self.width):
            print(count + 1, end=" ")
            # display numeric tile count
            
        print()
        
        char = ASCII_START_CHAR
            
        for y in range(self.height):
            print(chr(char), end=" ")
            # display alphabetic tile count 
            
            for x in range(self.width):
                print(self.board[x][y], end=" ")
                # display board tiles
            
            char += 1
            print()


def clear() -> None:
    """
    Clear console display.
    """
    
    os.system("cls" if os.name == "nt" else "clear")


def main() -> None:
    """
    Program entry point.
    """
    
    print("Welcome to Battleship Guru!\n")
    
    print("Start new game (N) or load existing game (L)?")
    start = input("> ").lower()
    # get starting input
    
    print("Enter game save file name")
    game_file = input("> ")
    # get game filename
    
    if start.lower() == "n":
    # start new game
    
        print("Enter the number of ships in game")
        num_ships = int(input("> "))
        # get ship count
        
        print("\nEnter the length of each ship:")
        
        ships = []

        for num in range(num_ships):
            ships.append(int(input(f"#{num} > ")))
            # get ship lengths
            
        game = Battleship(ships, MODE, GRID[0], GRID[1])
        # initialize Battleship game instance
        
    else:
        with open(os.path.join(DATA_DIR, game_file), "rb") as f:
            game = pickle.load(f)
            # load existing Battleship game instance from save file      
        
    game_over = False
    
    while not game_over:
        with open(os.path.join(DATA_DIR, game_file), "wb") as f:
            pickle.dump(game, f)
            # save Battleship game instance to file
    
        clear()
        game.predict()
        # predict next move
        
        print("Calculated move:\n")
        game.show()
        # display prediction on board
        
        print("\nInput result (x = hit, o = miss):")    
        res = ""
        
        while res != "x" and res != "o":
            res = input("> ").lower()
            # query move result
        
        game.update(res)
        # update game based upon move result

        if res == "x":
            print("Did this hit result in a ship sink? (Y/N)")
            sunk = input("> ").lower()
            # query if shink has been sunk
            
            if sunk == "y":
                print("Enter ship coordinates (ex: A1 A4)")
                coords = input("> ")
                # query sunk ship coordinates
                
                coords = coords.replace("(", "")
                coords = coords.replace(")", "")
                coords = coords.replace(",", " ")
                coords = coords.split()
                # parse sunk ship coordinate strings
                
                tile_1 = (
                    int(coords[0][1]) - 1,
                    ord(coords[0][0].upper()) - ASCII_START_CHAR       
                )
                # extract ship tile 1 from coordinate string
                
                tile_2 = (
                    int(coords[1][1]) - 1,
                    ord(coords[1][0].upper()) - ASCII_START_CHAR
                )
                # extract ship tile 2 from coordinate string
                
                game_over = game.sink(
                    tile_1[0], tile_1[1], tile_2[0], tile_2[1]
                )
                # sink ship
                
    print("\nGame over")
    os.remove(os.path.join(DATA_DIR, game_file))
    # remove Battleship game save file
    
    input()
    # wait until any input to exit
        

if __name__ == "__main__":
    main()