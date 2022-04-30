#!/usr/bin/env python
import requests
import random
import string
import time
import sys
import os


os.system("")  # enable ANSI escape codes on Windows.


TITLE = """
    _    _                                         
   | |  | |                                        
   | |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __  
   |  __  |/ _` | '_ \ / _` | '_ ` _ \ / _` | '_ \ 
   | |  | | (_| | | | | (_| | | | | | | (_| | | | |
   |_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                        __/ |                      
                       |___/   """


DICTIONARY_URL = "https://randomwordgenerator.com/json/words_ws.json"


"""        $
          www
         /. .\
        [  7  ]
     .___}~^~{___.
    (  |       |  )
    /  )\     /(  \
    ( { |     | } )
     `@ {_____} @'
        /  |  \ 
       (  /^\  )
       |  ) (  |
      /__/   \__\
"""


def timed(func):
    def inner(*args, **kwargs):
        start = time.time()
        out = func(*args, **kwargs)
        stop = time.time()
        return (out, stop - start)
    return inner


class Hangman:
    def __init__(self, wins=0, losses=0, is_replay=False, *args, **kwargs):
        if not is_replay:
            self.print_intro()
            self.best_time = None
        self.guesses = []
        self.chances = 6
        self.wins = wins
        self.losses = losses
        print(" Getting secret word... Please wait...", end='\r')
        self.secret_word = self.get_random_word().upper()
        self.clear_line()
        self.board = '_' * len(self.secret_word)
        self.head = """  $
                | ||           ,^.
                | ||          |   |
                | ||           `.' 
                | ||"""
        self.body = """
                | ||
                | ||
                | ||"""
        self.legs = """
                | ||
                | ||
                | ||
                | ||  _________________________"""
        if is_replay:
            for _ in range(38):
                self.clear_line()
                self.move_to_line_above()
            print("\033D", end='\r')  # scroll up a line
        self.print_board(is_replay)

    def print_intro(self):
        print(TITLE)

    def print_board(self, is_replay=False):
        alphabet = ' '.join(self.red(self.strikethrough(i)) if i in self.guesses else i for i in string.ascii_uppercase)
        padding = 8 * (len(self.secret_word) - self.board.count('_'))
        best = f"{self.best_time:.2f}" if self.best_time is not None else ""
        display = f"""                  _______________,,.
                 /_____________.;;'/|
                |"____  _______;;;]/                Wins: {self.wins}      Losses: {self.losses}      Best Time: {best} 
                | || //'        ;
                | ||//'         $
                | |//'          $
                |  /'         {self.head}
                | ||    {self.body}
                | ||    {self.legs}
                | || /                        /|
                | ||/           _____        / /
                | ||           /|___/       / /|
                | ||          / |  /       / /||
                |_|/         /__|_/       / / ||
               /                         / /| ||
              /                         / / | ||
             /                         / /  | |
            /_________________________/ /
            |_________________________|/             {' '.join(self.underline(i) if i != "_" else i for i in self.board):^{52 + padding}}
            | ||                    | ||       
            | ||                    | ||             {alphabet}
            | ||                    | ||
            | ||                    | ||
            | ||                    | |"""
        self.display_size = len(display.split('\n'))
        print(display)

    def get_random_word(self):
        page = requests.get(DICTIONARY_URL)
        if page.ok:
            try:
                data = page.json()
            except:  # simplejson.error.JSONDecodeError or json.JSONDecodeError
                raise Exception("Cannot access the random word dictionary!")
            if data.get("data", None) is not None:
                return data["data"][random.randint(0, len(data["data"]))]["word"]["value"]
        raise Exception("Cannot access the random word dictionary!")

    def get_guess(self):
        guess = input("Guess: ")  # on line 1
        # now on line 2
        if len(guess) != 1 or not guess.isalpha():
            self.move_to_line_above()  # now on line 1
            self.clear_line()  # clear line 1 ("Guess: blah")
            print("Invalid guess! Should be a single alphabetical character!")  # now on line 1
            # now on line 2
        while len(guess) != 1 or not guess.isalpha():            
            self.clear_line()  # clear if more than one iteration
            guess = input("Guess: ")  # now on line 3
            self.move_to_line_above()  # now on line 2
        # ends on line 2
        self.clear_line()
        self.move_to_line_above()  # now on line 1
        self.clear_line()
        return guess.upper()

    def start(self):
        did_win, round_time = self.play_round()
        if did_win:
            self.best_time = round_time
        self.refresh_board()
        print("You won!" if did_win else f"You died... The secret word was {self.secret_word}")
        replay = input("Would you like to play again? y/n: ").lower() in ['y', 'yes', 'yea']
        while replay:
            self.__init__(self.wins, self.losses, True)
            did_win, round_time = self.play_round()
            if self.best_time is not None and round_time < self.best_time and did_win:
                self.best_time = round_time
            elif self.best_time is None and did_win:
                self.best_time = round_time
            self.refresh_board()
            print("You won!" if did_win else f"You died... The secret word was {self.secret_word}")
            replay = input("Would you like to play again? y/n: ").lower() in ['y', 'yes', 'yea']

    @timed
    def play_round(self):
        did_win = False
        while self.chances > 0:
            guess = self.get_guess()
            if guess in self.guesses:
                continue
            self.guesses.append(guess)
            if guess not in self.secret_word:
                self.chances -= 1
                # draw next body part
                if self.chances == 5:
                    self.head = """  $
                | ||           www
                | ||          /. .\\
                | ||         [  7  ]
                | ||          }-^-{"""
                    
                elif self.chances == 4:
                    self.head = """  $
                | ||           www
                | ||          /. .\\
                | ||         [  7  ]
                | ||        __}-^-{__"""
                    self.body = """    |       |
                | ||         \     /
                | ||         |     |
                | ||         {_____}"""
                elif self.chances == 3:
                    self.head = """  $
                | ||           www
                | ||          /. .\\
                | ||         [  7  ]
                | ||      .___}-^-{__"""
                    self.body = """ (  |       |
                | ||     /  )\     /
                | ||     ( { |     |
                | ||      `@ {_____}"""
                elif self.chances == 2:
                    self.head += "_."
                    self.body = """ (  |       |  )
                | ||     /  )\     /(  \\
                | ||     ( { |     | } )
                | ||      `@ {_____} @'"""
                elif self.chances == 1:
                    self.legs = """     /  |
                | ||         (  /
                | ||        |  )
                | ||        /__/
                | ||  _________________________"""
                elif self.chances ==0:
                    self.legs = """     /  |  \\
                | ||         (  /^\\  )
                | ||        |  ) (  |
                | ||       /__/   \\__\\
                | ||  _________________________"""
                    self.head = self.head.replace('.', 'x', 2)
            else:
                self.board = self.assign_char_by_indices(self.board, guess, self.find_indices(self.secret_word, guess))
            if self.board == self.secret_word:
                self.wins += 1
                did_win = True
            self.refresh_board()
            if did_win:
                break
        else:  # lost
            self.losses += 1
            self.refresh_board()
        return did_win

    def refresh_board(self):
        for i in range(self.display_size):
            self.clear_line()
            self.move_to_line_above()
        self.print_board()

    @staticmethod
    def clear_line():
        print("\033[2K", end='\r')

    @staticmethod
    def move_to_line_above():
        print("\033[F", end='\r')

    @staticmethod
    def find_indices(string, char):
        return [i for i, letter in enumerate(string) if letter == char]

    @staticmethod
    def assign_char_by_indices(original_string, char, indices):
        return ''.join(char if i in indices else j for i, j in enumerate(original_string))

    @staticmethod
    def red(string):
        return f"\033[31m{string}\033[0m"

    @staticmethod
    def underline(string):
        return f"\033[4m{string}\033[0m"

    @staticmethod
    def strikethrough(string):
        return f"\033[9m{string}\033[0m"


def main():
    try:
        game = Hangman()
        game.start()
    except KeyboardInterrupt:
        print('\n\n')


if __name__ == "__main__":
    main()

