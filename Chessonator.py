    
# Chessonator 001
# By Ivan Igoshev
# Start date: 22nd of October 2019

depth_profile = [[99, 4],
                 [10, 5],
		         [4, 6]] # e.g. if number of pieces on the board is less or equals to 4, set the depth to 6

display_numbers = False

if True:
    players_text_file_path = './text files/players.txt'
    game_scenarios_text_file_path = './text files/game scenarios.txt'
    game_history_text_file_path = './text files/game history.txt'
    average_times_per_move_text_file_path = './text files/average times per move.txt'
    event_log_file_path = './text files/event log.txt'
    window_size_text_file_path = './text files/board size.txt'
    graphics_plath = './graphics/'

    pass # Paths

if True:
    
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # It hides the welcome message from the pygame library that would otherwise be shown in the console

    import sys # used to restart the program
    import pygame # library for GUI
    import concurrent.futures # library for multiprocessing
    from multiprocessing import freeze_support # to prevent it from opening a bunch of windows when running multiple processes and the py file is converted to an exe file
    import time # to measure the computer processing time and the time it takes the user to move.
    import datetime # for logs and game history
    import random # for selecting a random color for a player or for making a random move if a player runs out of time
    from copy import deepcopy # allows me to copy multidimensional arrays without any headaches
    import pygame.locals as pl # needed for a TextInput class
    import inspect # used to convert a function's name into string

    pass # Import

class TextInput:

    # Not my code
    # Copied from https://github.com/Nearoo/pygame-text-input

    """
    This class lets the user input a piece of text, e.g. a name or a message.
    This class let's the user input a short, one-lines piece of text at a blinking cursor
    that can be moved using the arrow-keys. Delete, home and end work as well.
    """
    def __init__(
            self,
            initial_string="", # <----- MODIFIED LINE
            #font_family="", # <----- MODIFIED LINE
            font_size=int(0.05 * 600), # <----- MODIFIED LINE board_size = 600
            antialias=True,
            text_color=(0, 0, 0),
            cursor_color=(0, 0, 1),
            repeat_keys_initial_ms=400,
            repeat_keys_interval_ms=35,
            max_string_length=-1):
        """
        :param initial_string: Initial text to be displayed
        :param font_family: name or list of names for font (see pygame.font.match_font for precise format)
        :param font_size:  Size of font in pixels
        :param antialias: Determines if antialias is applied to font (uses more processing power)
        :param text_color: Color of text (duh)
        :param cursor_color: Color of cursor
        :param repeat_keys_initial_ms: Time in ms before keys are repeated when held
        :param repeat_keys_interval_ms: Interval between key press repetition when held
        :param max_string_length: Allowed length of text
        """

        # Text related vars:
        self.antialias = antialias
        self.text_color = text_color
        self.font_size = font_size
        self.max_string_length = max_string_length
        self.input_string = initial_string  # Inputted text

        self.font_object = pygame.font.SysFont('arial', font_size) # <----- MODIFIED LINE

        self.size = self.font_object.size(self.input_string) # <----- MODIFIED LINE

        # Text-surface will be created during the first update call:
        self.surface = pygame.Surface((1, 1))
        self.surface.set_alpha(0)

        # Vars to make keydowns repeat after user pressed a key for some time:
        self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
        self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
        self.keyrepeat_interval_ms = repeat_keys_interval_ms

        # Things cursor:
        self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_size))
        self.cursor_surface.fill(cursor_color)
        self.cursor_position = len(initial_string)  # Inside text
        self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
        self.cursor_switch_ms = 500  # /|\
        self.cursor_ms_counter = 0

        self.clock = pygame.time.Clock()

    def update(self, events):

        self.size = self.font_object.size(self.input_string) # <----- MODIFIED LINE

        for event in events:
            if event.type == pygame.KEYDOWN:
                self.cursor_visible = True  # So the user sees where he writes

                # If none exist, create counter for that key:
                if event.key not in self.keyrepeat_counters:
                    self.keyrepeat_counters[event.key] = [0, event.unicode]

                if event.key == pl.K_BACKSPACE:
                    self.input_string = (
                        self.input_string[:max(self.cursor_position - 1, 0)]
                        + self.input_string[self.cursor_position:]
                    )

                    # Subtract one from cursor_pos, but do not go below zero:
                    self.cursor_position = max(self.cursor_position - 1, 0)
                elif event.key == pl.K_DELETE:
                    self.input_string = (
                        self.input_string[:self.cursor_position]
                        + self.input_string[self.cursor_position + 1:]
                    )

                elif event.key == pl.K_RETURN:
                    return True

                elif event.key == pl.K_RIGHT:
                    # Add one to cursor_pos, but do not exceed len(input_string)
                    self.cursor_position = min(self.cursor_position + 1, len(self.input_string))

                elif event.key == pl.K_LEFT:
                    # Subtract one from cursor_pos, but do not go below zero:
                    self.cursor_position = max(self.cursor_position - 1, 0)

                elif event.key == pl.K_END:
                    self.cursor_position = len(self.input_string)

                elif event.key == pl.K_HOME:
                    self.cursor_position = 0

                elif len(self.input_string) < self.max_string_length or self.max_string_length == -1:
                    # If no special key is pressed, add unicode of key to input_string
                    self.input_string = (
                        self.input_string[:self.cursor_position]
                        + event.unicode
                        + self.input_string[self.cursor_position:]
                    )
                    self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP

            elif event.type == pl.KEYUP:
                # *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
                if event.key in self.keyrepeat_counters:
                    del self.keyrepeat_counters[event.key]

        # Update key counters:
        for key in self.keyrepeat_counters:
            self.keyrepeat_counters[key][0] += self.clock.get_time()  # Update clock

            # Generate new key events if enough time has passed:
            if self.keyrepeat_counters[key][0] >= self.keyrepeat_intial_interval_ms:
                self.keyrepeat_counters[key][0] = (
                    self.keyrepeat_intial_interval_ms
                    - self.keyrepeat_interval_ms
                )

                event_key, event_unicode = key, self.keyrepeat_counters[key][1]
                pygame.event.post(pygame.event.Event(pl.KEYDOWN, key=event_key, unicode=event_unicode))

        # Re-render text surface:
        self.surface = self.font_object.render(self.input_string, self.antialias, self.text_color)

        # Update self.cursor_visible
        self.cursor_ms_counter += self.clock.get_time()
        if self.cursor_ms_counter >= self.cursor_switch_ms:
            self.cursor_ms_counter %= self.cursor_switch_ms
            self.cursor_visible = not self.cursor_visible

        if self.cursor_visible:
            cursor_y_pos = self.font_object.size(self.input_string[:self.cursor_position])[0]
            # Without this, the cursor is invisible when self.cursor_position > 0:
            if self.cursor_position > 0:
                cursor_y_pos -= self.cursor_surface.get_width()
            self.surface.blit(self.cursor_surface, (cursor_y_pos, 0))

        self.clock.tick()
        return False

    def get_surface(self):
        return self.surface

    def get_text(self):
        return self.input_string

    def get_size(self):
        return self.size

    def get_cursor_position(self):
        return self.cursor_position

    def set_text_color(self, color):
        self.text_color = color

    def set_cursor_color(self, color):
        self.cursor_surface.fill(color)

    def clear_text(self):
        self.input_string = ""
        self.cursor_position = 0

if True:

    def multiprocessed_minimax_depth_ZERO(max_depth, board, current_color, castling_info, move_history):
        # Depth zero only. Splits every branch into a separate thread

        # White - maximizing player
        # Black - minimizing player

        # Current_color:
        # True = white
        # False = black

        try:

            print("Minimax called with maximum depth {}".format(max_depth))
            
            results = []
            first_legal_move = True

            with concurrent.futures.ProcessPoolExecutor() as executor:

                if current_color == True: # if current_player == 'white' (maximizing player)

                    best_value = -2000

                    # Looks through every possible legal move
                    for current_position in range(64):

                        if board[current_position].islower():
                            legal_move_list = create_general_legal_move_list(board, current_position, True, castling_info)
                
                            for new_position in legal_move_list:

                                if first_legal_move: # Remember the 1st legal move
                                    best_current_pos = current_position
                                    best_new_pos = new_position
                                    first_legal_move = False
                                
                                new_board = board[:]
                                new_castling_info = castling_info[:]
                                make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
         
                                results.append(executor.submit(multiprocessed_minimax_depth_ONE, max_depth, new_board, False, new_castling_info, current_position, new_position))

                    for f in concurrent.futures.as_completed(results):

                        #print("Legal move: {} --> {}, guaranteed evaluation score: {}".format(f.result()[1], f.result()[2], f.result()[0]))

                        if f.result()[0] > best_value:
                            if max_depth > 5 and len(move_history) > 7:
                                # Simulates a move:
                                current_position = f.result()[1]
                                new_position = f.result()[2]
                                new_board = board[:]
                                new_castling_info = castling_info[:]
                                new_move_history = []
                                make_move(new_board, current_position, new_position, new_castling_info, new_move_history, False) # simulates a move, BUT simulation = False!! So that it would modify the new_move_history
                            
                                if not ((new_move_history[-1][:-2] == move_history[-4][:-2]) and (move_history[-1][:-2] == move_history[-5][:-2]) and (move_history[-2][:-2] == move_history[-6][:-2]) and (move_history[-3][:-2] == move_history[-7][:-2])):
                                    best_value = f.result()[0]
                                    best_current_pos = f.result()[1]
                                    best_new_pos = f.result()[2]
                            else:
                                best_value = f.result()[0]
                                best_current_pos = f.result()[1]
                                best_new_pos = f.result()[2]
                        
                else: # if current_player == False ('black', minimizing player)

                    best_value = 2000
                
                    # Looks through every possible legal move
                    for current_position in range(64):
                        if board[current_position].isupper():
                            legal_move_list = create_general_legal_move_list(board, current_position, False, castling_info)

                            for new_position in legal_move_list:

                                if first_legal_move: # Remember the 1st legal move
                                    best_current_pos = current_position
                                    best_new_pos = new_position
                                    first_legal_move = False

                                new_board = board[:]
                                new_castling_info = castling_info[:]
                                make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
                            
                                results.append(executor.submit(multiprocessed_minimax_depth_ONE, max_depth, new_board, True, new_castling_info, current_position, new_position))

                    for f in concurrent.futures.as_completed(results):

                        #print("Legal move: {} --> {}, guaranteed evaluation score: {}".format(f.result()[1], f.result()[2], f.result()[0]))

                        if f.result()[0] < best_value:
                            if max_depth > 5 and len(move_history) > 7:
                                # Simulates a move:
                                current_position = f.result()[1]
                                new_position = f.result()[2]
                                new_board = board[:]
                                new_castling_info = castling_info[:]
                                new_move_history = []
                                make_move(new_board, current_position, new_position, new_castling_info, new_move_history, False) # simulates a move, BUT simulation = False!! So that it would modify the new_move_history

                                if not ((new_move_history[-1][:-2] == move_history[-4][:-2]) and (move_history[-1][:-2] == move_history[-5][:-2]) and (move_history[-2][:-2] == move_history[-6][:-2]) and (move_history[-3][:-2] == move_history[-7][:-2])):
                                    best_value = f.result()[0]
                                    best_current_pos = f.result()[1]
                                    best_new_pos = f.result()[2]
                            else:
                                best_value = f.result()[0]
                                best_current_pos = f.result()[1]
                                best_new_pos = f.result()[2]
                            
            if max_depth < 6: # Do not go deeper than a depth of 6 (minimax can still be called with a depth of 7, but it will never shift automatically to a depth of 7)
                # If gets caught in an infinite loop, run minimax with a higher depth
                if len(move_history) > 7:
                    # Simulates a move:
                    new_board = board[:]
                    new_castling_info = castling_info[:]
                    new_move_history = []
                    make_move(new_board, best_current_pos, best_new_pos, new_castling_info, new_move_history, False) # simulates a move, BUT simulation = False!! So that it would modify the new_move_history

                    if (new_move_history[-1][:-2] == move_history[-4][:-2]) and (move_history[-1][:-2] == move_history[-5][:-2]) and (move_history[-2][:-2] == move_history[-6][:-2]) and (move_history[-3][:-2] == move_history[-7][:-2]):
                        # If gets caught in an infinite loop, run minimax with a depth of 6
                        return multiprocessed_minimax_depth_ZERO(6, board, current_color, castling_info, move_history)
                             
            return best_current_pos, best_new_pos, best_value

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def multiprocessed_minimax_depth_ONE(max_depth, board, current_color, castling_info, argument_1, argument_2):
        # Normal minimax, only to be called for a currennt depth of 1 when minimax is multiprocessed. 
        # It takes 2 additional arguments: current_position, new_position and returns them untouched.
        # This data is useful when analyzing data from all threads.

        # White - maximizing player
        # Black - minimizing player

        # Current_color:
        # True = white
        # False = black

        try:

            alpha = -2000
            beta = 2000
            depth = 1

            # if leaf node, return evaluation score
            if max_depth == 1: # if max depth reached
                #print("{}".format(depth), end = "")
                return evaluate(board, current_color, castling_info, depth), argument_1, argument_2

            elif current_color == True: # if current_player == 'white' (maximizing player)

                best_value = -2000

                no_legal_moves = True

                # Looks through every possible legal move
                for current_position in range(64):

                    if board[current_position].islower():
                        legal_move_list = create_general_legal_move_list(board, current_position, True, castling_info)

                        for new_position in legal_move_list:

                            no_legal_moves = False

                            new_board = board[:]
                            new_castling_info = castling_info[:]
                            make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
         
                            evaluation_score = multiprocessed_minimax_depth_TWO_OR_MORE(2, max_depth, new_board, False, new_castling_info, alpha, beta)

                            if evaluation_score > best_value:
                                best_value = evaluation_score

                            #if best_value >= beta:
                            #    return best_value, argument_1, argument_2

                            #if best_value > alpha:
                            #    alpha = best_value

            else: # if current_player == False ('black', minimizing player)

                best_value = 2000

                no_legal_moves = True

                # Looks through every possible legal move
                for current_position in range(64):
                    if board[current_position].isupper():
                        legal_move_list = create_general_legal_move_list(board, current_position, False, castling_info)

                        for new_position in legal_move_list:

                            no_legal_moves = False

                            new_board = board[:]
                            new_castling_info = castling_info[:]
                            make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
                    
                            evaluation_score = multiprocessed_minimax_depth_TWO_OR_MORE(2, max_depth, new_board, True, new_castling_info, alpha, beta)

                            if evaluation_score < best_value:
                                best_value = evaluation_score

                            #if best_value <= alpha:
                            #    return best_value, argument_1, argument_2

                            #if best_value < beta:
                            #    beta = best_value

            if no_legal_moves:
                #print("(simulated game ended at depth {}) ".format(depth), end = "")
                return evaluate(board, current_color, castling_info, depth), argument_1, argument_2
        
            return best_value, argument_1, argument_2

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def multiprocessed_minimax_depth_TWO_OR_MORE(depth, max_depth, board, current_color, castling_info, alpha, beta):
        # Plain minimax, but does not return the best move (current and new positins) for efficiency reasons
        # Not suitable for depth 0

        # When minimax is multiprocessed, this function is only used starting from depth 2

        # White - maximizing player
        # Black - minimizing player

        # Current_color:
        # True = white
        # False = black

        try:

            # if leaf node, return evaluation score
            if depth == max_depth: # if max depth reached
                #print("{}".format(depth), end = "")
                return evaluate(board, current_color, castling_info, depth)

            elif current_color == True: # if current_player == 'white' (maximizing player)

                best_value = -2000

                no_legal_moves = True

                # Looks through every possible legal move
                for current_position in range(64):

                    if board[current_position].islower():
                        legal_move_list = create_general_legal_move_list(board, current_position, True, castling_info)

                        for new_position in legal_move_list:

                            no_legal_moves = False

                            new_board = board[:]
                            new_castling_info = castling_info[:]
                            make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
         
                            evaluation_score = multiprocessed_minimax_depth_TWO_OR_MORE((depth + 1), max_depth, new_board, False, new_castling_info, alpha, beta)

                            if evaluation_score > best_value:
                                best_value = evaluation_score

                            #if best_value >= beta:
                            #    return best_value

                            #if best_value > alpha:
                            #    alpha = best_value

            else: # if current_player == False ('black', minimizing player)

                best_value = 2000

                no_legal_moves = True

                # Looks through every possible legal move
                for current_position in range(64):
                    if board[current_position].isupper():
                        legal_move_list = create_general_legal_move_list(board, current_position, False, castling_info)

                        for new_position in legal_move_list:

                            no_legal_moves = False

                            new_board = board[:]
                            new_castling_info = castling_info[:]
                            make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
                    
                            evaluation_score = multiprocessed_minimax_depth_TWO_OR_MORE((depth + 1), max_depth, new_board, True, new_castling_info, alpha, beta)

                            if evaluation_score < best_value:
                                best_value = evaluation_score

                            #if best_value <= alpha:
                            #    return best_value

                            #if best_value < beta:
                            #    beta = best_value

            if no_legal_moves:
                #print("(simulated game ended at depth {}) ".format(depth), end = "")
                return evaluate(board, current_color, castling_info, depth)
        
            return best_value

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)
      
    def generate_evaluation_scores_for_every_legal_move_with_multiprocessed_minimax(max_depth, board, current_color, castling_info, move_history):
        # Depth zero only. Splits every branch into a separate thread

        # White - maximizing player
        # Black - minimizing player

        # Current_color:
        # True = white
        # False = black

        try:

            print("Minimax called with maximum depth {}".format(max_depth))

            results = []
            move_and_evaluation_score_list = []
        
            with concurrent.futures.ProcessPoolExecutor() as executor:

                if current_color == True: # if current_player == 'white' (maximizing player)

                    # Looks through every possible legal move
                    for current_position in range(64):

                        if board[current_position].islower():
                            legal_move_list = create_general_legal_move_list(board, current_position, True, castling_info)
                
                            for new_position in legal_move_list:

                                new_board = board[:]
                                new_castling_info = castling_info[:]
                                make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
         
                                results.append(executor.submit(multiprocessed_minimax_depth_ONE, max_depth, new_board, False, new_castling_info, current_position, new_position))

                else: # if current_player == False ('black', minimizing player)

                    # Looks through every possible legal move
                    for current_position in range(64):
                        if board[current_position].isupper():
                            legal_move_list = create_general_legal_move_list(board, current_position, False, castling_info)

                            for new_position in legal_move_list:

                                new_board = board[:]
                                new_castling_info = castling_info[:]
                                make_move(new_board, current_position, new_position, new_castling_info, None, True) # simulates a move
                            
                                results.append(executor.submit(multiprocessed_minimax_depth_ONE, max_depth, new_board, True, new_castling_info, current_position, new_position))

                for f in concurrent.futures.as_completed(results):
                    move_and_evaluation_score_list.append([f.result()[0], f.result()[1], f.result()[2]])

            return sort_evaluation_scores_for_every_legal_move_list(move_and_evaluation_score_list, current_color)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # Minimax

if True:
    def evaluate(board, current_color, castling_info, depth):
        # Good old evaluation function

        # Current_color:
        # True = white
        # False = black

        try:

            game_outcome = calculate_game_outcome(board, current_color, castling_info)
            if game_outcome == -1: # checkmate, black wins
                return - (1999 - depth) # takes away the depth to favour the checkmate with the least number of moves
            elif game_outcome == 1: # checkmate, white wins
                return (1999 - depth)
            elif game_outcome in [2, 3]: # stalemate, no check and no legal moves
                return 0

            evaluation_score = 0

            evaluation_score += find_no_of_points(board, True)
            evaluation_score -= find_no_of_points(board, False)

            return evaluation_score

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def find_no_of_points(board, current_color):
        
        try:

            # Piece-square tables and material value
            if True:

                # Piece-square tables are for a White player
                # They need to be reversed to be used for a Black player

                if number_of_pieces_on_board(board) > 10:
                    king_piece_square_table = [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                                               -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                                               -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                                               -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                                               -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
                                               -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
                                               +2.0, +2.0, +0.0, +0.0, +0.0, +0.0, +2.0, +2.0,
                                               +2.0, +3.0, +1.0, +0.0, +0.0, +1.0, +3.0, +2.0]
                else: # Endgame
                    king_piece_square_table = [-5.0, -4.0, -4.0, -4.0, -4.0, -4.0, -4.0, -5.0,
                                               -4.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -4.0,
                                               -4.0, -3.0, +0.0, +0.0, +0.0, +0.0, -3.0, -4.0,
                                               -4.0, -3.0, +0.0, +1.0, +1.0, +0.0, -3.0, -4.0,
                                               -4.0, -3.0, +0.0, +1.0, +1.0, +0.0, -3.0, -4.0,
                                               -4.0, -3.0, +0.0, +0.0, +0.0, +0.0, -3.0, -4.0,
                                               -4.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -4.0,
                                               -5.0, -4.0, -4.0, -4.0, -4.0, -4.0, -4.0, -5.0]

                    ## White king under attack
                    #king_position = find_king_position(board, True)
                    #if piece_under_attack(board, None, None, king_position, True, False):
                    #    evaluation_score -= 15

                    ## Black king under attack
                    #king_position = find_king_position(board, False)
                    #if piece_under_attack(board, None, None, king_position, False, False):
                    #    evaluation_score += 15

                # WARNING: rows in the QUEEN table are not symmetrical
                queen_piece_square_table = [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
                                            -1.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, -1.0,
                                            -1.0, +0.0, +0.5, +0.5, +0.5, +0.5, +0.0, -1.0,
                                            -0.5, +0.0, +0.5, +0.5, +0.5, +0.5, +0.0, -0.5,
                                            +0.0, +0.0, +0.5, +0.5, +0.5, +0.5, +0.0, -0.5, # asymmetry
                                            -1.0, +0.5, +0.5, +0.5, +0.5, +0.5, +0.0, -1.0, # asymmetry
                                            -1.0, +0.0, +0.5, +0.0, +0.0, +0.0, +0.0, -1.0, # asymmetry
                                            -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
    
                rook_piece_square_table = [+0.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0,
                                           +0.5, +1.0, +1.0, +1.0, +1.0, +1.0, +1.0, +0.5,
                                           -0.5, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, -0.5,
                                           -0.5, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, -0.5,
                                           -0.5, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, -0.5,
                                           -0.5, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, -0.5,
                                           -0.5, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, -0.5,
                                           +0.0, +0.0, +0.0, +0.5, +0.5, +0.0, +0.0, +0.0]
    
                bishop_piece_square_table = [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
                                             -1.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, -1.0,
                                             -1.0, +0.0, +0.5, +1.0, +1.0, +0.5, +0.0, -1.0,
                                             -1.0, +0.5, +0.5, +1.0, +1.0, +0.5, +0.5, -1.0,
                                             -1.0, +0.0, +1.0, +1.0, +1.0, +1.0, +0.0, -1.0,
                                             -1.0, +1.0, +1.0, +1.0, +1.0, +1.0, +1.0, -1.0,
                                             -1.0, +0.5, +0.0, +0.0, +0.0, +0.0, +0.5, -1.0,
                                             -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
    
                knight_piece_square_table = [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
                                             -4.0, -2.0, +0.0, +0.0, +0.0, +0.0, -2.0, -4.0,
                                             -3.0, +0.0, +1.0, +1.5, +1.5, +1.0, +0.0, -3.0,
                                             -3.0, +0.5, +1.5, +2.0, +2.0, +1.5, +0.5, -3.0,
                                             -3.0, +0.0, +1.5, +2.0, +2.0, +1.5, +0.0, -3.0,
                                             -3.0, +0.5, +1.0, +1.5, +1.5, +1.0, +0.5, -3.0,
                                             -4.0, -2.0, +0.0, +0.5, +0.5, +0.0, -2.0, -4.0,
                                             -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
    
                pawn_piece_square_table = [+0.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0,
                                           +5.0, +5.0, +5.0, +5.0, +5.0, +5.0, +5.0, +5.0,
                                           +1.0, +1.0, +2.0, +3.0, +3.0, +2.0, +1.0, +1.0,
                                           +0.5, +0.5, +1.0, +2.5, +2.5, +1.0, +0.5, +0.5,
                                           +0.0, +0.0, +0.0, +2.0, +2.0, +0.0, +0.0, +0.0,
                                           +0.5, -0.5, -1.0, +0.0, +0.0, -1.0, -0.5, +0.5,
                                           +0.5, +1.0, +1.0, -2.0, -2.0, +1.0, +1.0, +0.5,
                                           +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0, +0.0]

                # lower case is white, upper case is black
                material_value = {'p': 10,
                                  'n': 35,
                                  'b': 35,
                                  'r': 52.5,
                                  'q': 100,
                                  'k': 0,
                                  'P': 10,
                                  'N': 35,
                                  'B': 35,
                                  'R': 52.5,
                                  'Q': 100,
                                  'K': 0}

            evaluation_score = 0

            for position in range(64):
                piece = board[position]
                if not piece == '-' and ((current_color == True and piece.islower()) or (current_color == False and piece.isupper())):

                    evaluation_score += material_value[piece]
                    if True: # Use of Piece-square tables:
                        if piece == 'p':
                            evaluation_score += pawn_piece_square_table[position]
                        elif piece == 'P':
                            evaluation_score += pawn_piece_square_table[63 - position]
                        elif piece == 'n':
                            evaluation_score += knight_piece_square_table[position]
                        elif piece == 'N':
                            evaluation_score += knight_piece_square_table[63 - position]
                        elif piece == 'b':
                            evaluation_score += bishop_piece_square_table[position]
                        elif piece == 'B':
                            evaluation_score += bishop_piece_square_table[63 - position]
                        elif piece == 'r':
                            evaluation_score += rook_piece_square_table[position]
                        elif piece == 'R':
                            evaluation_score += rook_piece_square_table[63 - position]
                        elif piece == 'q':
                            evaluation_score += queen_piece_square_table[position]
                        elif piece == 'Q':
                            evaluation_score += queen_piece_square_table[70 - position - 2 * ((63 - position) % 8)] # <-- explanation below
                            # The funny formula above takes the position away from 63 and then mirrors it in its row
                            # It is needed because Queen's piece-square table is not symmetrical in terms of rows
                            # Therefore, if position == 9, it would return 49 instead of 54
                            # This formula is a simplification of the following function:
                            #def find(position):
                            #    a = 63 - position
                            #    b = a % 8
                            #    c = a - b
                            #    d = 7 - b
                            #    e = c + d
                            #    return e
                        elif piece == 'k':
                            evaluation_score += king_piece_square_table[position]
                        else: # piece == 'K'
                            evaluation_score += king_piece_square_table[63 - position]

            return evaluation_score

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def calculate_game_outcome(board, current_color, castling_info):
    
        # Outputs:
        #  0 - keep playing
        #  1 - checkmate, White wins
        # -1 - checkmate, Black wins
        #  2 - stalemate (not check, but no legal moves)
        #  3 - draw

        # Special cases: (not returned by this function)
        #  4 - forfeit
        #  5 - player runs out of time
    
        # Current_color:
        # True = white
        # False = black

        try:

            # Draw if three moves are repeated
            #try:
            #   if (move_history[-1] == move_history[-5] == move_history[-9]) and (move_history[-2] == move_history[-6] == move_history[-10]) and (move_history[-3] == move_history[-7] == move_history[-11]) and (move_history[-4] == move_history[-8] == move_history[-12]):
            #        return 3
            #except:
            #    pass

            king_position = find_king_position(board, current_color)

            for position in range(64):
                # if selected cell contains a piece of the player's color AND there is a legal move, it is not a check mate
                if (not board[position] == '-') and ((current_color == True and board[position].islower()) or (current_color == False and board[position].isupper())) and not create_general_legal_move_list(board, position, current_color, castling_info) == []:
                    return 0
            # if there are no legal moves:
            if piece_under_attack(board, 0, 0, king_position, current_color, False):
                if current_color == False: # Checkmate to Black --> White wins
                    return 1
                else: # current_color == True: # Checkmate to White --> Black wins
                    return -1
            else:
                return 2

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def number_of_pieces_on_board(board):

        try:

            n = 0
            for piece in board:
                if not piece == '-':
                    n += 1
            return n

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def sort_evaluation_scores_for_every_legal_move_list(List, current_color):
        # Bubble soort
        # If White, then sort in descending order
        # If Black, then sort in ascending order

        try:

            for index_1 in range(len(List)):
                for index_2 in range(len(List)):
                    if index_2 > index_1 and ((List[index_2][0] > List[index_1][0] and current_color == True) or (List[index_2][0] < List[index_1][0] and current_color == False)):
                        List[index_1], List[index_2] = List[index_2], List[index_1] # Swap

            return List

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def get_depth_from_depth_profile(board):

        try:

            n = number_of_pieces_on_board(board)

            for item in depth_profile:
                if n <= item[0]:
                    max_depth = item[1]

            return max_depth

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # Minimax support functions

# If you can read this, stop hacking my code

def quit_program():
    try:
        # Quits the program
        pygame.quit()
        quit()
    except:
        pass

if True:
    def initiate_and_fill_window_and_display_logo(board_size):

        try:

            width = int(3 * board_size)
            height = int(1.481 * board_size)
            pygame.init()
            gameDisplay = pygame.display.set_mode((width , height)) # initiates the window and defines its size
            pygame.display.set_caption('Chessonator') # name on the header
            pygame.Surface.fill(gameDisplay, (255, 255, 255)) # fills the window with white

            img = pygame.image.load(graphics_plath + 'LOGO.png')
            img = pygame.transform.scale(img, (int(1.25 * board_size), int(0.231 * board_size)))
            gameDisplay.blit(img, [int(0.875 * board_size), 0, int(1.25 * board_size), int(0.231 * board_size)])

            return gameDisplay

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def display_text(text, x_coord, y_coord, color, font_size, allign):

        try:

            color_assign = {'black': (0, 0, 0),
                            'red': (255, 0, 0),
                            'dark brown': (177, 82, 25),
                            'pink': (231, 81, 198)}

            color = color_assign[color]

            largeText = pygame.font.SysFont('arial', int(font_size * board_size))
            #largeText = pygame.font.Font(None, int(font_size * board_size))
            TextSurf = largeText.render(text, True, color)
            TextRect = TextSurf.get_rect()

            if allign == 'centre':
                TextRect.center = x_coord, y_coord
                gameDisplay.blit(TextSurf, TextRect)
            elif allign == 'left':
                TextRect = TextSurf.get_rect()
                gameDisplay.blit(TextSurf, [x_coord, y_coord])

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_board_GUI(board, board_size, cell_size, current_position, computer_current_position, computer_new_position, legal_move_list, upside_down):
        # Refreshes the board GUI

        try:
            
            x_coord = int(0.875 * board_size) # in pixels
            y_coord = int(0.231 * board_size) # in pixels
            counter = 1 # this counter is needed to allocate the color to the cells.
            # counter does not count all cells directly - when moving from one line to another it is incremented twice
            if not upside_down:
                position = 0 # position of a certain cell in a 1D array
            else:
                position = 63

            column_to_letter = {0: '',
                                1: 'A',
                                2: 'B',
                                3: 'C',
                                4: 'D',
                                5: 'E',
                                6: 'F',
                                7: 'G',
                                8: 'H',
                                9: ''}

            # Displaying cells (individual squares on the game board), assigning colors
            for a in range(10):
                for b in range(10):
                    if a in [0, 9]: # row 0 or 9
                        pygame.draw.rect(gameDisplay, (255, 255, 255), [x_coord, y_coord, cell_size, cell_size]) # White (Background for coordinates)
                        text = column_to_letter[b] if not upside_down else column_to_letter[9 - b]
                        display_text(text, (x_coord + int(cell_size / 2)), (y_coord + int(cell_size / 2)), 'dark brown', 0.08, 'centre')
                    elif b in [0, 9]: # column 0 or 9
                        pygame.draw.rect(gameDisplay, (255, 255, 255), [x_coord, y_coord, cell_size, cell_size]) # White (Background for coordinates)
                        text = str(9 - a) if not upside_down else str(a)
                        display_text(text, (x_coord + int(cell_size / 2)), (y_coord + int(cell_size / 2)), 'dark brown', 0.08, 'centre')
                    else: # withing the board
                        if position == current_position:
                            pygame.draw.rect(gameDisplay, (194, 91, 95), [x_coord, y_coord, cell_size, cell_size]) # Red (Cell with a selected piece)
                        elif position == computer_current_position:
                            pygame.draw.rect(gameDisplay, (255, 0, 0), [x_coord, y_coord, cell_size, cell_size]) # Red (Computer's previous position)
                        elif position == computer_new_position:
                            pygame.draw.rect(gameDisplay, (255, 0, 0), [x_coord, y_coord, cell_size, cell_size]) # Red (Computer's new position)
                        elif position in legal_move_list and counter % 2 == 0:
                            pygame.draw.rect(gameDisplay, (107, 212, 136), [x_coord, y_coord, cell_size, cell_size]) # Light Green (Legal move onto a white cell)
                        elif position in legal_move_list:
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [x_coord, y_coord, cell_size, cell_size]) # Dark Green (Legal move onto a black cell)
                        elif position == 2 and (101 in legal_move_list):
                            pygame.draw.rect(gameDisplay, (107, 212, 136), [x_coord, y_coord, cell_size, cell_size]) # Light Green (Black queenside castling)
                        elif position == 6 and (102 in legal_move_list):
                            pygame.draw.rect(gameDisplay, (107, 212, 136), [x_coord, y_coord, cell_size, cell_size]) # Light Green (Black kingside castling)
                        elif position == 58 and (103 in legal_move_list):
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [x_coord, y_coord, cell_size, cell_size]) # Dark Green (White queenside castling)
                        elif position == 62 and (104 in legal_move_list):
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [x_coord, y_coord, cell_size, cell_size]) # Dark Green (White kingside castling)
                        elif counter % 2 == 0:
                            pygame.draw.rect(gameDisplay, (252, 221, 174), [x_coord, y_coord, cell_size, cell_size]) # Light brown (Empty white cell)
                        else:
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [x_coord, y_coord, cell_size, cell_size]) # Dark brown (Empty black cell)

                        if not board[position] == '-':
                            piece = board[position]
                            piece_color = 'B' if piece.isupper() else 'W' # Detects the color of the piece
                            # Retrieves and image for a particular piece
                            img = pygame.image.load(graphics_plath + piece_color.upper() + piece.upper() + '.png')
                            img = pygame.transform.scale(img, (cell_size, cell_size))
                            gameDisplay.blit(img, [x_coord, y_coord, cell_size, cell_size])

                        if display_numbers:
                            text = str(position)
                            display_text(text, (x_coord + int(cell_size / 2)), (y_coord + int(cell_size / 2)), 'pink', 0.05, 'centre')

                        counter += 1
                        if not upside_down:
                            position += 1
                        else:
                            position -= 1

                    x_coord += cell_size

                x_coord = int(0.875 * board_size)
                y_coord += cell_size
                counter += 1

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_welcoming_window(board_size, play_against_a_computer_button_is_selected, play_against_a_human_button_is_selected, play_a_game_scenario_is_selected, see_the_game_history_button_is_selected, minus_button_is_selected, plus_button_is_selected):
    
        try:

            # ERASE / WHITE FILL
            if True:
                # Fills everything to the right of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
                # Fills everything to the left of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])

            # PLAY AGAINST A COMPUTER BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.225 * board_size), int(0.2162 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not play_against_a_computer_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.2082 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.3082 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.2082 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.842 * board_size), int(0.2082 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.2132 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.3132 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.2132 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.847 * board_size), int(0.2132 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Play against a computer'
                display_text(text, int(2.5375 * board_size), int(0.2662 * board_size), 'black', 0.03, 'centre')

            # PLAY AGAINST A HUMAN BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.225 * board_size), int(0.5324 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not play_against_a_human_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.5244 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.6244 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.5244 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.842 * board_size), int(0.5244 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.5294 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.6294 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.5294 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.847 * board_size), int(0.5294 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Play against a human'
                display_text(text, int(2.5375 * board_size), int(0.5824 * board_size), 'black', 0.03, 'centre')

            # PLAY A GAME SCENARIO BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.225 * board_size), int(0.8486 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not play_a_game_scenario_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.8406 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.9406 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(0.8406 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.842 * board_size), int(0.8406 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.8456 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.9456 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(0.8456 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.847 * board_size), int(0.8456 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Play a game scenario'
                display_text(text, int(2.5375 * board_size), int(0.8986 * board_size), 'black', 0.03, 'centre')

            # SEE THE GAME HISTORY BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.225 * board_size), int(1.1648 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not see_the_game_history_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.1568 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.2568 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.1568 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.842 * board_size), int(1.1568 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.1618 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.2618 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.1618 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.847 * board_size), int(1.1618 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'See the game history'
                display_text(text, int(2.5375 * board_size), int(1.2148 * board_size), 'black', 0.03, 'centre')

            # WINDOW SIZE ADJUSTMENT
            if True:
                # TEXT
                if True:
                    text = 'Adjust the window size:'
                    display_text(text, int(0.25 * board_size), int(1.2 * board_size), 'black', 0.04, 'centre')

                # MINUS BUTTON
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.125 * board_size), int(1.256 * board_size), int(0.1 * board_size), int(0.1 * board_size)])
                    if not minus_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.117 * board_size), int(1.248 * board_size), int(0.116 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.117 * board_size), int(1.348 * board_size), int(0.116 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.117 * board_size), int(1.248 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.217 * board_size), int(1.248 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.122 * board_size), int(1.253 * board_size), int(0.106 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.122 * board_size), int(1.353 * board_size), int(0.106 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.122 * board_size), int(1.253 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.222 * board_size), int(1.253 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = '–'
                    display_text(text, int(0.175 * board_size), int(1.296 * board_size), 'black', 0.10, 'centre')

                # PLUS BUTTON
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.275 * board_size), int(1.256 * board_size), int(0.1 * board_size), int(0.1 * board_size)])
                    if not plus_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.267 * board_size), int(1.248 * board_size), int(0.116 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.267 * board_size), int(1.348 * board_size), int(0.116 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.267 * board_size), int(1.248 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.367 * board_size), int(1.248 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.272 * board_size), int(1.253 * board_size), int(0.106 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.272 * board_size), int(1.353 * board_size), int(0.106 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.272 * board_size), int(1.253 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.372 * board_size), int(1.253 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = '+'
                    display_text(text, int(0.322 * board_size), int(1.302 * board_size), 'black', 0.10, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_setup_window_human_vs_computer(board_size, selected_color, selected_time_limit, selected_cheat_limit, go_back_button_is_selected, go_to_game_button_is_selected, selected_name, new_name_is_visible, delete_selected_name_right_button_is_selected, delete_selected_name_button_is_visible):

        try:

            # ERASE / WHITE FILL
            if True:
                # Fills everything to the right of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
                # Fills everything to the left of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])
                # Fills the board with white (erases the board)
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.231 * board_size), int(1.25 * board_size), int(1.25 * board_size)])

            # TOP BUTTONS
            if True:
                # DELETE SELECTED NAME BUTTON (RIGHT)
                if delete_selected_name_button_is_visible:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.3125 * board_size), int(0.131 * board_size), int(0.5 * board_size), int(0.10 * board_size)])
                    if not delete_selected_name_right_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3045 * board_size), int(0.123 * board_size), int(0.512 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3045 * board_size), int(0.223 * board_size), int(0.512 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3045 * board_size), int(0.123 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.8045 * board_size), int(0.123 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3095 * board_size), int(0.128 * board_size), int(0.506 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3095 * board_size), int(0.228 * board_size), int(0.506 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3095 * board_size), int(0.128 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.8095 * board_size), int(0.128 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Delete selected name'
                    display_text(text, int(2.5625 * board_size), int(0.181 * board_size), 'black', 0.03, 'centre')

            # COLOR CHOICE
            if True:
                text = 'What colour would you like to play for?'
                display_text(text, int(1.5 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')
                # Color choice white fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(1.125 * board_size), int(0.35 * board_size), int(0.75 * board_size), int(0.10 * board_size)])
                # Color choice top boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.122 * board_size), int(0.347 * board_size), int(0.756 * board_size), int(0.006 * board_size)])
                # Color choice bottom boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.122 * board_size), int(0.447 * board_size), int(0.756 * board_size), int(0.006 * board_size)])
                # Color choice 1st vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.122 * board_size), int(0.347 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Color choice 2nd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.372 * board_size), int(0.347 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Color choice 3rd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.622 * board_size), int(0.347 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Color choice 1st vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.872 * board_size), int(0.347 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                if selected_color == 'white':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.125 * board_size), int(0.35 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.342 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.442 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.342 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.368 * board_size), int(0.342 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_color == 'black':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.375 * board_size), int(0.35 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.342 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.442 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.342 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.618 * board_size), int(0.342 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_color == 'random':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.625 * board_size), int(0.35 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.342 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.442 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.342 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.868 * board_size), int(0.342 * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                text = 'WHITE'
                display_text(text, int(1.25 * board_size), int(0.4 * board_size), 'black', 0.03, 'centre')
                text = 'BLACK'
                display_text(text, int(1.5 * board_size), int(0.4 * board_size), 'black', 0.03, 'centre')
                text = 'RANDOM'
                display_text(text, int(1.75 * board_size), int(0.4 * board_size), 'black', 0.03, 'centre')

            # TIME LIMIT
            if True:
                text = 'What time limit per move would you like to set?'
                display_text(text, int(1.5 * board_size), int(0.6 * board_size), 'black', 0.05, 'centre')
                # Time limit choice white fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.6565 * board_size), int(1.25 * board_size), int(0.10 * board_size)])
                # Time limit choice top boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.6535 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice bottom boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.7535 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice 1st vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 2nd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.122 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 3rd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.372 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 4th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.622 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 5th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.872 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 6th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.122 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                if selected_time_limit == 'unlimited':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(0.875 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '10 seconds':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.125 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '30 seconds':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.375 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '1 minute':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.625 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '2 minutes':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.875 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.117 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                text = 'UNLIMITED'
                display_text(text, int(1 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '10 seconds'
                display_text(text, int(1.25 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '30 seconds'
                display_text(text, int(1.5 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '1 minute'
                display_text(text, int(1.75 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '2 minutes'
                display_text(text, int(2 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')

            # CHEAT LIMIT
            if True:
                text = 'What cheat limit would you like to set?'
                display_text(text, int(1.5 * board_size), int(0.9065 * board_size), 'black', 0.05, 'centre')
                # Cheat limit choice white fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.963 * board_size), int(1.25 * board_size), int(0.10 * board_size)])
                # Time limit choice top boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.96 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice bottom boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(1.06 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice 1st vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 2nd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.122 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 3rd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.372 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 4th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.622 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 5th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.872 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 6th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.122 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                if selected_cheat_limit == 'unlimited':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(0.875 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == 'no cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.125 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == '5 cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.375 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == '10 cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.625 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == '20 cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.875 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.117 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                text = 'UNLIMITED'
                display_text(text, int(1 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = 'no cheats'
                display_text(text, int(1.25 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = '5 cheats'
                display_text(text, int(1.5 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = '10 cheats'
                display_text(text, int(1.75 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = '20 cheats'
                display_text(text, int(2 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')

            # NAME SELECTION (ON THE RIGHT)
            if True:
                text = 'What is your name?'
                display_text(text, int(2.5625 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')

                list_of_names = get_list_of_names()
                list_of_names_copy = list_of_names[:]
                if not new_name_is_visible:
                    list_of_names_copy.remove('New name')

                difference = 0
                for name in list_of_names_copy:
                    # Fill
                    if difference == 0 or (difference == 0.1 and new_name_is_visible):
                        fill_color = (252, 221, 174) # First two cells ('play as a guest' and 'new name') are filled with tan
                    else:
                        fill_color = (255, 255, 255) # White otherwise
                    pygame.draw.rect(gameDisplay, fill_color, [int(2.25 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.247 * board_size), int((0.347 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.247 * board_size), int((0.447 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.247 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.872 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    difference += 0.1

                difference = 0
                for name in list_of_names_copy:
                    if name == selected_name:
                        # Fill
                        pygame.draw.rect(gameDisplay, (137, 205, 156), [int(2.25 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.242 * board_size), int((0.342 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.242 * board_size), int((0.442 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.242 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.867 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                    text = name
                    display_text(text, int(2.5625 * board_size), int((0.4 + difference) * board_size), 'black', 0.03, 'centre')

                    difference += 0.1

            # BOTTOM BUTTONS
            if True:
                # Left button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.875 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_back_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.117 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.122 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Go back'
                    display_text(text, int(1 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

                # Right button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.875 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_to_game_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.117 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.122 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Start the game'
                    display_text(text, int(2 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_setup_window_human_vs_human(board_size, selected_time_limit, selected_cheat_limit, go_back_button_is_selected, go_to_game_button_is_selected, selected_name_white_player, selected_name_black_player, delete_selected_name_right_button_is_selected, delete_selected_name_left_button_is_selected, delete_selected_name_button_is_visible, new_name_is_visible):
    
        try:

            # ERASE / WHITE FILL
            if True:
                # Fills everything to the right of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
                # Fills everything to the left of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])
                # Fills the board with white (erases the board)
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.231 * board_size), int(1.25 * board_size), int(1.25 * board_size)])

            # TOP BUTTONS
            if True:
                # DELETE SELECTED NAME BUTTON (LEFT)
                if delete_selected_name_button_is_visible:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.1875 * board_size), int(0.131 * board_size), int(0.5 * board_size), int(0.10 * board_size)])
                    if not delete_selected_name_left_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.1795 * board_size), int(0.123 * board_size), int(0.512 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.1795 * board_size), int(0.223 * board_size), int(0.512 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.1795 * board_size), int(0.123 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.6795 * board_size), int(0.123 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.1845 * board_size), int(0.128 * board_size), int(0.506 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.1845 * board_size), int(0.228 * board_size), int(0.506 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.1845 * board_size), int(0.128 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.6845 * board_size), int(0.128 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Delete selected name'
                    display_text(text, int(0.4375 * board_size), int(0.181 * board_size), 'black', 0.03, 'centre')

                # DELETE SELECTED NAME BUTTON (RIGHT)
                if delete_selected_name_button_is_visible:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.3125 * board_size), int(0.131 * board_size), int(0.5 * board_size), int(0.10 * board_size)])
                    if not delete_selected_name_right_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3045 * board_size), int(0.123 * board_size), int(0.512 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3045 * board_size), int(0.223 * board_size), int(0.512 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3045 * board_size), int(0.123 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.8045 * board_size), int(0.123 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3095 * board_size), int(0.128 * board_size), int(0.506 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3095 * board_size), int(0.228 * board_size), int(0.506 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.3095 * board_size), int(0.128 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.8095 * board_size), int(0.128 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Delete selected name'
                    display_text(text, int(2.5625 * board_size), int(0.181 * board_size), 'black', 0.03, 'centre')

            # TIME LIMIT
            if True:
                text = 'What time limit per move would you like to set?'
                display_text(text, int(1.5 * board_size), int(0.6 * board_size), 'black', 0.05, 'centre')
                # Time limit choice white fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.6565 * board_size), int(1.25 * board_size), int(0.10 * board_size)])
                # Time limit choice top boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.6535 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice bottom boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.7535 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice 1st vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 2nd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.122 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 3rd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.372 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 4th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.622 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 5th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.872 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 6th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.122 * board_size), int(0.6535 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                if selected_time_limit == 'unlimited':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(0.875 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '10 seconds':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.125 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '30 seconds':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.375 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '1 minute':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.625 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_time_limit == '2 minutes':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.875 * board_size), int(0.6565 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.6485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.7485 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.117 * board_size), int(0.6485 * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                text = 'UNLIMITED'
                display_text(text, int(1 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '10 seconds'
                display_text(text, int(1.25 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '30 seconds'
                display_text(text, int(1.5 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '1 minute'
                display_text(text, int(1.75 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')
                text = '2 minutes'
                display_text(text, int(2 * board_size), int(0.7065 * board_size), 'black', 0.03, 'centre')

            # CHEAT LIMIT
            if True:
                text = 'What cheat limit would you like to set?'
                display_text(text, int(1.5 * board_size), int(0.9065 * board_size), 'black', 0.05, 'centre')
                # Cheat limit choice white fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.963 * board_size), int(1.25 * board_size), int(0.10 * board_size)])
                # Time limit choice top boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.96 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice bottom boundary
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(1.06 * board_size), int(1.256 * board_size), int(0.006 * board_size)])
                # Time limit choice 1st vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.872 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 2nd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.122 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 3rd vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.372 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 4th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.622 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 5th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.872 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                # Time limit choice 6th vertical boundary from the left
                pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.122 * board_size), int(0.96 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                if selected_cheat_limit == 'unlimited':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(0.875 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.867 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == 'no cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.125 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.117 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == '5 cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.375 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.367 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == '10 cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.625 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.617 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                elif selected_cheat_limit == '20 cheats':
                    # Fill
                    pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.875 * board_size), int(0.963 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.955 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(1.055 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.867 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.117 * board_size), int(0.955 * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                text = 'UNLIMITED'
                display_text(text, int(1 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = 'no cheats'
                display_text(text, int(1.25 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = '5 cheats'
                display_text(text, int(1.5 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = '10 cheats'
                display_text(text, int(1.75 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')
                text = '20 cheats'
                display_text(text, int(2 * board_size), int(1.013 * board_size), 'black', 0.03, 'centre')

            # NAME SELECTION - WHITE (ON THE LEFT)
            if True:
                text = "What is White player's name?"
                display_text(text, int(0.4375 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')

                list_of_names = get_list_of_names()
                list_of_names_copy = list_of_names[:]
                if not new_name_is_visible:
                    list_of_names_copy.remove('New name')

                difference = 0
                for name in list_of_names_copy:
                    if not name == 'Play as a guest':
                        # Fill
                        if difference == 0 and new_name_is_visible:
                            fill_color = (252, 221, 174) # First two cells ('play as a guest' and 'new name') are filled with tan
                        else:
                            fill_color = (255, 255, 255) # White otherwise
                        pygame.draw.rect(gameDisplay, fill_color, [int(0.125 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.122 * board_size), int((0.347 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.122 * board_size), int((0.447 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.122 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.747 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                        difference += 0.1

                difference = 0
                for name in list_of_names_copy:
                    if not name == 'Play as a guest':
                        if name == selected_name_white_player:
                            # Fill
                            pygame.draw.rect(gameDisplay, (137, 205, 156), [int(0.125 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.117 * board_size), int((0.342 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.117 * board_size), int((0.442 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.117 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(0.742 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                        text = name
                        display_text(text, int(0.4375 * board_size), int((0.4 + difference) * board_size), 'black', 0.03, 'centre')

                        difference += 0.1

            # NAME SELECTION - BLACK (ON THE RIGHT)
            if True:
                text = "What is Black player's name?"
                display_text(text, int(2.5625 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')

                list_of_names = get_list_of_names()
                list_of_names_copy = list_of_names[:]
                if not new_name_is_visible:
                    list_of_names_copy.remove('New name')

                difference = 0
                for name in list_of_names_copy:
                    if not name == 'Play as a guest':
                        # Fill
                        if difference == 0 and new_name_is_visible:
                            fill_color = (252, 221, 174) # First two cells ('play as a guest' and 'new name') are filled with tan
                        else:
                            fill_color = (255, 255, 255) # White otherwise
                        pygame.draw.rect(gameDisplay, fill_color, [int(2.25 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.247 * board_size), int((0.347 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.247 * board_size), int((0.447 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.247 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(2.872 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                        difference += 0.1

                difference = 0
                for name in list_of_names_copy:
                    if not name == 'Play as a guest':
                        if name == selected_name_black_player:
                            # Fill
                            pygame.draw.rect(gameDisplay, (137, 205, 156), [int(2.25 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.242 * board_size), int((0.342 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.242 * board_size), int((0.442 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.242 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (63, 161, 91), [int(2.867 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                        text = name
                        display_text(text, int(2.5625 * board_size), int((0.4 + difference) * board_size), 'black', 0.03, 'centre')

                        difference += 0.1

            # BOTTOM BUTTONS
            if True:
                # Left button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.875 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_back_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.117 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.122 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Go back'
                    display_text(text, int(1 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

                # Right button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.875 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_to_game_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.117 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.122 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Start the game'
                    display_text(text, int(2 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_scenario_selection_window(board_size, selected_scenario, delete_button_is_selected, create_new_scenario_button_is_selected, go_back_button_is_selected, go_to_game_button_is_selected, delete_button_is_visible, create_new_scenario_button_is_visible):

        try:

            # Fills everything to the right of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills everything to the left of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills the board with white (erases the board)
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.231 * board_size), int(1.25 * board_size), int(1.25 * board_size)])

            # SCENARIO NAME SELECTION
            if True:
                if create_new_scenario_button_is_visible:
                    text = 'Select a game scenario or create a new one.'
                else:
                    text = 'Select a game scenario. You will have to delete one of the saved game scenarios to create a new one.'
                display_text(text, int(1.5 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')

                game_scenarios = get_game_scenarios()

                difference = 0
                for scenario in game_scenarios:
                    # Fill
                    fill_color = (255, 255, 255) # White
                    pygame.draw.rect(gameDisplay, fill_color, [int(1.1875 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.1845 * board_size), int((0.347 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.1845 * board_size), int((0.447 + difference) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.1845 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (0, 0, 0), [int(1.8095 * board_size), int((0.347 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    difference += 0.1

                difference = 0
                for index, scenario in enumerate(game_scenarios):
                    if index == selected_scenario:
                        # Fill
                        pygame.draw.rect(gameDisplay, (137, 205, 156), [int(1.1875 * board_size), int((0.35 + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.1795 * board_size), int((0.342 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.1795 * board_size), int((0.442 + difference) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.1795 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (63, 161, 91), [int(1.8045 * board_size), int((0.342 + difference) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                    text = scenario[0]
                    display_text(text, int(1.5 * board_size), int((0.4 + difference) * board_size), 'black', 0.03, 'centre')

                    difference += 0.1

            # BOTTOM BUTTONS
            if True:
                # 1. Go back button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.875 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_back_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.867 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.117 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.872 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.122 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Go back'
                    display_text(text, int(1 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

                # 2. Delete button
                if delete_button_is_visible:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.20833 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not delete_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.20033 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.20033 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.20033 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.45033 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.20533 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.20533 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.20533 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.45533 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Delete scenario'
                    display_text(text, int(1.33333 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

                # 3. Create new scenario button
                if create_new_scenario_button_is_visible:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.54167 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not create_new_scenario_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.53367 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.53367 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.53367 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.78367 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.53867 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.53867 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.53867 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.78867 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Create new scenario'
                    display_text(text, int(1.66667 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

                # 4. Start the game button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.875 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_to_game_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.867 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.117 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.872 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.122 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Start the game'
                    display_text(text, int(2 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_create_game_scenario_elements(board_size, current_position, deleted_piece, legal_move_list, go_back_button_is_selected, play_against_a_computer_button_is_selected, play_against_a_human_button_is_selected):

        try:

            # ERASE / WHITE FILL
            if True:
                # Fills everything to the right of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
                # Fills everything to the left of the board with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])

            # SIGN
            if True:
                text = 'Place the pieces onto the board.'
                display_text(text, int(0.4375 * board_size), int(0.4185 * board_size), 'black', 0.05, 'centre')

            # DRAW SMALL 5x2 BOARD ON THE LEFT
            if True:
                cell_size = int(board_size / 8)

                x_coord = int(0.125 * board_size) # in pixels
                y_coord = int(0.481 * board_size) # in pixels
                counter = 0 # this counter is needed to allocate the color to the cells.
                # counter does not count all cells directly - when moving from one line to another it is incremented twice
                position = 0

                small_board = ['q', 'r', 'b', 'n', 'p', 'Q', 'R', 'B', 'N', 'P']

                for a in range(2):
                    for b in range(5):

                        if position + 64 == current_position:
                            pygame.draw.rect(gameDisplay, (194, 91, 95), [x_coord, y_coord, cell_size, cell_size]) # Red (Cell with a selected piece)
                        elif counter % 2 == 0:
                            pygame.draw.rect(gameDisplay, (252, 221, 174), [x_coord, y_coord, cell_size, cell_size]) # Light brown (Empty white cell)
                        else:
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [x_coord, y_coord, cell_size, cell_size]) # Dark brown (Empty black cell)

                        piece = small_board[position]
                        piece_color = 'B' if piece.isupper() else 'W' # Detects the color of the piece
                        # Retrieves and image for a particular piece
                        img = pygame.image.load(graphics_plath + piece_color.upper() + piece.upper() + '.png')
                        img = pygame.transform.scale(img, (cell_size, cell_size))
                        gameDisplay.blit(img, [x_coord, y_coord, cell_size, cell_size])

                        counter += 1
                        position += 1
                        x_coord += cell_size

                    x_coord = int(0.125 * board_size)
                    y_coord += cell_size

            # DRAW THE TRASH CAN TILE
            if True:
                cell_size = int(board_size / 8)

                x_coord = int(0.375 * board_size) # in pixels
                y_coord = int(0.856 * board_size) # in pixels

                if 74 in legal_move_list:
                    pygame.draw.rect(gameDisplay, (107, 212, 136), [x_coord, y_coord, cell_size, cell_size]) # Light Green (Legal move onto a white cell)
                else:
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [x_coord, y_coord, cell_size, cell_size]) # Light brown (Empty white cell)

                if deleted_piece == None:
                    # Retrieves and image for a trash can
                    img = pygame.image.load(graphics_plath + 'trashcan.png')
                else:
                    piece = deleted_piece
                    piece_color = 'B' if piece.isupper() else 'W' # Detects the color of the piece
                    # Retrieves and image for a particular piece
                    img = pygame.image.load(graphics_plath + piece_color.upper() + piece.upper() + '.png')

                img = pygame.transform.scale(img, (cell_size, cell_size))
                gameDisplay.blit(img, [x_coord, y_coord, cell_size, cell_size])

            # GO BACK BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.15 * board_size), int(1.22475 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not go_back_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.142 * board_size), int(1.21675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.142 * board_size), int(1.31675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.142 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.767 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.147 * board_size), int(1.22175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.147 * board_size), int(1.32175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.147 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.772 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Go back'
                display_text(text, int(0.4625 * board_size), int(1.27475 * board_size), 'black', 0.03, 'centre')

            # PLAY AGAINST A COMPUTER BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.225 * board_size), int(1.07475 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not play_against_a_computer_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.06675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.16675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.06675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.842 * board_size), int(1.06675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.07475 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.17475 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.07475 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.847 * board_size), int(1.07475 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Play against a computer'
                display_text(text, int(2.5375 * board_size), int(1.12475 * board_size), 'black', 0.03, 'centre')

            # PLAY AGAINST A HUMAN BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.225 * board_size), int(1.22475 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not play_against_a_human_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.21675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.31675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.217 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.842 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.22175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.32175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.222 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.847 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Play against a human'
                display_text(text, int(2.5375 * board_size), int(1.27475 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_scenario_name_input_window(board_size, ok_button_is_selected, ok_button_is_visible, textinput):

        try:

            # Fills everything to the right of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills everything to the left of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills the board with white (erases the board)
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.231 * board_size), int(1.25 * board_size), int(1.25 * board_size)])
        
            # SIGN
            if True:
                text = 'Please give a name to this new game scenario:'
                display_text(text, int(1.5 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')

            # TEXT INPUT
            if True:

                xoffset, yoffset = textinput.get_size()

                # Blit its surface onto the screen
                gameDisplay.blit(textinput.get_surface(), (int(1.5 * board_size - (xoffset / 2)), int(0.4185 * board_size - (yoffset / 2))))

            # BOTTOM BUTTONS
            if True:
                # OK button
                if ok_button_is_visible:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.375 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not ok_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.617 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.622 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'OK'
                    display_text(text, int(1.5 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_new_name_input_window(board_size, ok_button_is_selected, ok_button_is_visible, textinput):

        try:

            # Fills everything to the right of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills everything to the left of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills the board with white (erases the board)
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.231 * board_size), int(1.25 * board_size), int(1.25 * board_size)])
        
            # SIGN
            if True:
                text = 'What is your name?'
                display_text(text, int(1.5 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')

            # TEXT INPUT
            if True:

                xoffset, yoffset = textinput.get_size()

                # Blit its surface onto the screen
                gameDisplay.blit(textinput.get_surface(), (int(1.5 * board_size - (xoffset / 2)), int(0.4185 * board_size - (yoffset / 2))))

            # BOTTOM ERROR SIGN
            if True:
                list_of_names = get_list_of_names()
                if textinput.get_text() in list_of_names or textinput.get_text() == 'Computer': # If name already registered
                    text = 'This name is already registered'
                    display_text(text, int(1.5 * board_size), int(0.5435 * board_size), 'red', 0.05, 'centre')

            # BOTTOM BUTTONS
            if True:
                # OK button
                if ok_button_is_visible:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.375 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not ok_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.617 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.622 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Save'
                    display_text(text, int(1.5 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_game_history_window(board_size, go_back_button_is_selected, game_history, y):

        try:

            # Fills everything to the right of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills everything to the left of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills the board with white (erases the board)
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.231 * board_size), int(1.25 * board_size), int(1.25 * board_size)])

            # TABLE
            if True:

                difference = 0
                for n in range(0, len(game_history) + 1):
                    
                    # Fill
                    if True:
                        if n == 0:
                            # Background fill of an entire row (tan)
                            pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.4375 * board_size), int(y * board_size), int(2.125 * board_size), int(0.10 * board_size)])
                        else:
                            # Background fill of only leftmost and rightmost cells (tan)
                            # Left
                            pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.4375 * board_size), int((y + difference) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                            # Right
                            pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.2625 * board_size), int((y + difference) * board_size), int(0.3 * board_size), int(0.10 * board_size)])

                    # Draw boundaries
                    if True:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.4345 * board_size), int((y - 0.003 + difference) * board_size), int(2.131 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.4345 * board_size), int((y + 0.1 - 0.003 + difference) * board_size), int(2.131 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (0, 0, 0), [int(0.4345 * board_size), int((y - 0.003 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                        for x in range(6):
                            # Other vertical boundaries
                            pygame.draw.rect(gameDisplay, (0, 0, 0), [int((1.0595 + x * 0.3) * board_size), int((y - 0.003 + difference) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    # Fill text
                    if True:

                        if n == 0:

                            #text = ["Player's name", 'Average time per move', 'Percentage of victories against the computer', 'Percentage of victories against other players', 'Percentage of victories overall', 'List of all games played']
                        
                            text = "Player's name:"
                            display_text(text, int(0.75 * board_size), int((y + 0.05) * board_size), 'black', 0.035, 'centre')

                            text = 'Average time'
                            display_text(text, int(1.2125 * board_size), int((y + 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'per move:'
                            display_text(text, int(1.2125 * board_size), int((y + 0.1 - 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'Victories against'
                            display_text(text, int(1.5125 * board_size), int((y + 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'the computer:'
                            display_text(text, int(1.5125 * board_size), int((y + 0.1 - 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'Victories against'
                            display_text(text, int(1.8125 * board_size), int((y + 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'other players:'
                            display_text(text, int(1.8125 * board_size), int((y + 0.1 - 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'Overall percentage'
                            display_text(text, int(2.1125 * board_size), int((y + 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'of victories:'
                            display_text(text, int(2.1125 * board_size), int((y + 0.1 - 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'Lists of all'
                            display_text(text, int(2.4125 * board_size), int((y + 0.033) * board_size), 'black', 0.035, 'centre')

                            text = 'games played:'
                            display_text(text, int(2.4125 * board_size), int((y + 0.1 - 0.033) * board_size), 'black', 0.035, 'centre')

                        else:
                       
                            display_text(game_history[n - 1][0], int(0.75 * board_size), int(((y + 0.05) + difference) * board_size), 'black', 0.03, 'centre')
                            for x in range(5):
                                display_text(game_history[n - 1][x + 1], int((1.2125 + x * 0.3) * board_size), int(((y + 0.05) + difference) * board_size), 'black', 0.03, 'centre')

                    difference += 0.1

            # BOTTOM BUTTONS
            if True:
                # Go back button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.375 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_back_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.617 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.622 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Go back'
                    display_text(text, int(1.5 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_list_of_games_window(board_size, go_back_button_is_selected, previous_page_button_is_selected, next_page_button_is_selected, player_name, selected_page_no, list_of_games_pages):

        try:

            # Fills everything to the right of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills everything to the left of the board with white to erase previous contents
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(1.481 * board_size)])
            # Fills the board with white (erases the board)
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.231 * board_size), int(1.25 * board_size), int(1.25 * board_size)])
            
            # Fills a small bar on top above the logo (to erase a small part of the game history table)
            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.2 * board_size), int(1.25 * board_size), int(0.031 * board_size)])

            # TOP TEXT
            if True:
                text = 'These are all games played by ' + player_name + ':   (page {}/{})'.format((selected_page_no + 1), len(list_of_games_pages))
                display_text(text, int(1.5 * board_size), int(0.2935 * board_size), 'black', 0.05, 'centre')

            # SENTENCES
            if True:
                sentences = list_of_games_pages[selected_page_no]

                y = 0.4

                difference = 0
                for sentence in sentences:
                    
                    display_text(sentence, int(1.5 * board_size), int((y + difference) * board_size), 'black', 0.033, 'centre')

                    difference += 0.05

            # BOTTOM BUTTONS
            if True:

                # Previous page button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.025 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not previous_page_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.017 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.017 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.017 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.267 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.022 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.022 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.022 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.272 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Previous page'
                    display_text(text, int(1.15 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

                # Next page button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.375 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not next_page_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.367 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.617 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.372 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.622 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Next page'
                    display_text(text, int(1.5 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

                # Go back button
                if True:
                    # Fill
                    pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.725 * board_size), int(1.2695 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                    if not go_back_button_is_selected:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.717 * board_size), int(1.2615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.717 * board_size), int(1.3615 * board_size), int(0.262 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.717 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.967 * board_size), int(1.2615 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    else:
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.722 * board_size), int(1.2665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.722 * board_size), int(1.3665 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.722 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.972 * board_size), int(1.2665 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                    text = 'Go back'
                    display_text(text, int(1.85 * board_size), int(1.3195 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_gameplay_buttons(board_size, forfeit_button_is_selected, exit_button_is_selected, flip_the_board_button_is_selected, undo_a_move_button_is_selected):
    
        try:

            # ERASE / WHITE FILL
            if True:
                # Fills the left-top corner of the window with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(0.231 * board_size)])
                # Fills the right with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(0.231 * board_size)])

            # FORFEIT BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.125 * board_size), int(0.0655 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                if not forfeit_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.117 * board_size), int(0.0575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.117 * board_size), int(0.1575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.117 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.367 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.122 * board_size), int(0.0625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.122 * board_size), int(0.1625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.122 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.372 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Forfeit'
                display_text(text, int(0.25 * board_size), int(0.1155 * board_size), 'black', 0.03, 'centre')

            # EXIT BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.5 * board_size), int(0.0655 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                if not exit_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.492 * board_size), int(0.0575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.492 * board_size), int(0.1575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.492 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.742 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.497 * board_size), int(0.0625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.497 * board_size), int(0.1625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.497 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.747 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Exit'
                display_text(text, int(0.625 * board_size), int(0.1155 * board_size), 'black', 0.03, 'centre')

            # FLIP THE BOARD BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.25 * board_size), int(0.0655 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                if not flip_the_board_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.242 * board_size), int(0.0575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.242 * board_size), int(0.1575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.242 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.492 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.247 * board_size), int(0.0625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.247 * board_size), int(0.1625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.247 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.497 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Flip the board'
                display_text(text, int(2.375 * board_size), int(0.1155 * board_size), 'black', 0.03, 'centre')

            # UNDO A MOVE BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.625 * board_size), int(0.0655 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                if not undo_a_move_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.617 * board_size), int(0.0575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.617 * board_size), int(0.1575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.617 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.867 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.622 * board_size), int(0.0625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.622 * board_size), int(0.1625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.622 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.872 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Undo a move'
                display_text(text, int(2.75 * board_size), int(0.1155 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_computer_is_thinking(board_size):

        try:

            # ERASE / WHITE FILL
            if True:
                # Fills the left-top corner of the window with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(0.231 * board_size)])
                # Fills the right with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(0.231 * board_size)])

            # DISPLAY TEXT
            if True:
                text = 'Computer is thinking'
                display_text(text, int(0.4375 * board_size), int(0.1155 * board_size), 'red', 0.05, 'centre')
                text = 'Please wait'
                display_text(text, int(2.5625 * board_size), int(0.1155 * board_size), 'red', 0.05, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board):

        try:

            line_spacing = 0.015
            how_are_the_points_calculated_button_y_coords = 999
            show_the_move_history_button_y_coords = 999

            # DRAW GAME STATISTICS WINDOW
            if True:
                # Feedback window fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.0625 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(1.1875 * board_size)])
                # Feedback window top  
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # Feedback window bottom boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(1.4035 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # Feedback window left boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Feedback window right boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.86 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Fill - dark brown (same as on chess board)
                # Boundary - light brown (same as on chess board)

                y_pos = 0.31

                text = 'Game statistics'
                display_text(text, int(0.46875 * board_size), int(y_pos * board_size), 'dark brown', 0.08, 'centre')

                y_pos += 0.04
                y_pos += line_spacing

            # First line - move counter and the player's name
            if True:
                if state == 'next player':
                    text = ("{}. This is {}'s turn.".format(str(move_counter), player[not current_color]))
                else: # state == 'transition to human player moved':
                    text = ("{}. This is {}'s turn.".format(str(move_counter), player[current_color]))
                display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.035, 'left')
                y_pos += 0.035
                y_pos += line_spacing

            # Player info
            if True:
                white_points = find_no_of_points(board, True)
                text = ('{} (White): {} points'.format(player[True], white_points))
                display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.035, 'left')
                y_pos += 0.035
                y_pos += line_spacing

                if not player[True] == 'Computer':

                    if not average_time_per_move_white == None:
                        if not average_time_per_move_white // 60 == 0:
                            text = ('Average time per move: {}min {}s'.format(int(average_time_per_move_white // 60), round(average_time_per_move_white % 60), 1)) # Display as minutes + seconds
                        else:
                            text = ('Average time per move: {}s'.format(average_time_per_move_white)) # Display as seconds only
                        display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                        y_pos += 0.025
                        y_pos += line_spacing

                    if not cheat_limit == 0:
                        if not cheat_limit == None:
                            text = ('Cheats used: {}/{}'.format(cheat_counter_white, cheat_limit))
                        else:
                            text = ('Cheats used: {}'.format(cheat_counter_white))
                        display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                        y_pos += 0.025
                        y_pos += line_spacing

                black_points = find_no_of_points(board, False)
                text = ('{} (Black): {} points'.format(player[False], black_points))
                display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.035, 'left')
                y_pos += 0.035
                y_pos += line_spacing

                if not player[False] == 'Computer':

                    if not average_time_per_move_black == None:
                        if not average_time_per_move_black // 60 == 0:
                            text = ('Average time per move: {}min {}s'.format(int(average_time_per_move_black // 60), round(average_time_per_move_black % 60), 1)) # Display as minutes + seconds
                        else:
                            text = ('Average time per move: {}s'.format(average_time_per_move_black)) # Display as seconds only
                        display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                        y_pos += 0.025
                        y_pos += line_spacing

                    if not cheat_limit == 0:
                        if not cheat_limit == None:
                            text = ('Cheats used: {}/{}'.format(cheat_counter_black, cheat_limit))
                        else:
                            text = ('Cheats used: {}'.format(cheat_counter_black))
                        display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                        y_pos += 0.025
                        y_pos += line_spacing

                y_pos += 0.01

            # How are the points calculated? BUTTON
            if not state == 'turn passed to a computer':
                # Fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.15625 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not how_are_the_points_calculated_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.14825 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.14825 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.14825 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.77325 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.15507 * board_size), int((y_pos - 0.003) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.15507 * board_size), int((y_pos + 0.097) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.15507 * board_size), int((y_pos - 0.003) * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.78007 * board_size), int((y_pos - 0.003) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'How are the points calculated?'
                display_text(text, int(0.46875 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                how_are_the_points_calculated_button_y_coords = y_pos

                y_pos += 0.1
                y_pos += line_spacing

            # Last move / Your move line(s)
            if True:
                if not move_history == []:

                    sentence = write_move_with_prefix(state, player, move_history)

                    text_lines = split_text_into_lines(sentence, 0.7125)

                    for text in text_lines:

                        display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                        y_pos += 0.025
                        y_pos += line_spacing

                y_pos += 0.01

            # Show the move history BUTTON
            if not state == 'turn passed to a computer':
                # Fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.15625 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not show_the_move_history_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.14825 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.14825 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.14825 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.77325 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.15507 * board_size), int((y_pos - 0.003) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.15507 * board_size), int((y_pos + 0.097) * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.15507 * board_size), int((y_pos - 0.003) * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.78007 * board_size), int((y_pos - 0.003) * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Show the move history'
                display_text(text, int(0.46875 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                show_the_move_history_button_y_coords = y_pos

                y_pos += 0.1
                y_pos += line_spacing

            # Captured pieces
            if True:
                if not move_history == [] and not move_history[-1][-2] == []:

                    text = 'Captured pieces:'
                    display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.035, 'left')
                    y_pos += 0.035
                    y_pos += line_spacing

                    captured_pieces = sort_captured_pieces(move_history[-1][-2])

                    n = 0
                    x_pos = 0.10875

                    for piece in captured_pieces:
                        piece_color = 'B' if piece.isupper() else 'W' # Detects the color of the piece
                        # Retrieves and image for a particular piece
                        img = pygame.image.load('./graphics/' + piece_color + piece + '.png')
                        img = pygame.transform.scale(img, (int(0.08 * board_size), int(0.08 * board_size)))
                        gameDisplay.blit(img, [int(x_pos * board_size), int(y_pos * board_size), int(0.08 * board_size), int(0.08 * board_size)])

                        if n == 8:
                            n = 0
                            x_pos = 0.10875
                            y_pos += 0.08
                        else:
                            n += 1
                            x_pos += 0.08

            ## Remaining time
            #if state in ['waiting for 1st click', 'waiting for 2nd click'] and (not start_time == None):
            #    now_time = time.time()
            #    time_since_beginning_of_move = round(now_time - start_time, 2)

            #    text = str(time_since_beginning_of_move)

            #    display_text(text, int(0.46875 * board_size), int(1.3485 * board_size), 'black', 0.035, 'centre')
            #    print(text)

            return how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_remaining_time(board_size, state, start_time, time_limit):

        #try:
        if True:

            if not time_limit == None:

                # Background fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.0775 * board_size), int(1.3085 * board_size), int(0.7825 * board_size), int(0.08 * board_size)])

                remaining_time = int(time_limit + start_time - time.time())

                if remaining_time < 0:
                    remaining_time = 0

                if remaining_time % 60 < 10:
                    text = '0' + str(remaining_time // 60) + ':0' + str(remaining_time % 60)
                else:
                    text = '0' + str(remaining_time // 60) + ':' + str(remaining_time % 60)

                display_text(text, int(0.46875 * board_size), int(1.3485 * board_size), 'red', 0.08, 'centre')

    def refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance):

        try:

            line_spacing = 0.015
            what_move_should_i_make_y_pos = 999
            what_other_move_could_i_make_y_pos = 999

            #selected_feedback_options = [False, False, False, False]
            # selected_feedback_options:
            # [Why did {name} make this move?,
            #  What move should I make?,
            #  Was that a strong move?,
            #  What other move could I make?]

            # DRAW FEEDBACK WINDOW
            if True:
                # Feedback window fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.125 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(1.1875 * board_size)])
                # Feedback window top  
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.125 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # Feedback window bottom boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.125 * board_size), int(1.4035 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # Feedback window left boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.125 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Feedback window right boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.9225 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Fill - dark brown (same as on chess board)
                # Boundary - light brown (same as on chess board)

                y_pos = 0.31

                text = 'Feedback'
                display_text(text, int(2.53125 * board_size), int(y_pos * board_size), 'dark brown', 0.08, 'centre')

                y_pos += 0.04
                y_pos += line_spacing
                y_pos += line_spacing
                y_pos += line_spacing

            # Why did {name} make this move?
            if not move_history == []:
                if state == 'next player':
                    feedbacks[0] = None
                    selected_feedback_options[0] = False # this feedback option is not selected

                    # Draw a button for 'Why did {name} make this move?' feedback option
                    if True:
                        # Fill
                        pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                        y_pos += 0.05

                        if player[current_color] == 'Computer':
                            text = 'Why did a computer make this move?'
                        else:
                            text = ('Why did {} make this move?'.format(player[current_color]))
                        display_text(text, int(2.53125 * board_size), int((y_pos) * board_size), 'black', 0.03, 'centre')


                        y_pos += 0.015
                        y_pos += line_spacing

                        y_pos += line_spacing
                        y_pos += line_spacing
                        y_pos += line_spacing
                        y_pos += line_spacing

                elif state in ['waiting for 1st click', 'waiting for 2nd click']:
                    if selected_feedback_options[0] == False: # if this option is not selected, draw the button again

                        # Draw a button for 'Why did {name} make this move?' feedback option
                        if True:
                            # Fill
                            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                            y_pos += 0.05

                            if player[not current_color] == 'Computer':
                                text = 'Why did a computer make this move?'
                            else:
                                text = ('Why did {} make this move?'.format(player[not current_color]))
                            display_text(text, int(2.53125 * board_size), int((y_pos) * board_size), 'black', 0.03, 'centre')

                            y_pos += 0.015
                            y_pos += line_spacing

                    else:

                        text_lines = feedbacks[0]
                    
                        window_height = 0.05 + 0.015 + line_spacing + (len(text_lines) * (0.025 + line_spacing)) + line_spacing
                    
                        # Draw a 'Why did {name} make this move?' feedback window
                        if True:
                            # Fill
                            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(window_height * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + window_height - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                    
                            y_pos += 0.05

                            if player[not current_color] == 'Computer':
                                text = 'Why did a computer make this move?'
                            else:
                                text = ('Why did {} make this move?'.format(player[not current_color]))
                            display_text(text, int(2.53125 * board_size), int((y_pos) * board_size), 'black', 0.03, 'centre')

                            y_pos += 0.015
                            y_pos += line_spacing

                            for text in text_lines:
                                display_text(text, int(2.2675 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                                y_pos += 0.025
                                y_pos += line_spacing

                    y_pos += line_spacing
                    y_pos += line_spacing
                    y_pos += line_spacing
                    y_pos += line_spacing

            # What move should I make?
            if True:
                if state == 'next player':
                    feedbacks[1] = None
                    selected_feedback_options[1] = False # this feedback option is not selected

                    what_move_should_i_make_y_pos = y_pos

                    # Draw a button for a feedback option
                    if True:
                        # Fill
                        pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                        text = 'What move should I make?'
                        display_text(text, int(2.53125 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                elif state in ['waiting for 1st click', 'waiting for 2nd click']:
                    if selected_feedback_options[1] == False: # if this option is not selected, draw the button again

                        what_move_should_i_make_y_pos = y_pos

                        # Draw a button for a feedback option
                        if True:
                            # Fill
                            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                            text = 'What move should I make?'
                            display_text(text, int(2.53125 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                    else:

                        text_lines = feedbacks[1]

                        window_height = 0.05 + 0.015 + line_spacing + (len(text_lines) * (0.025 + line_spacing)) + line_spacing
                    
                        what_move_should_i_make_y_pos = y_pos

                        # Draw a feedback window
                        if True:
                            # Fill
                            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(window_height * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + window_height - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                    
                            y_pos += 0.05

                            text = 'What move should I make?'
                            display_text(text, int(2.53125 * board_size), int((y_pos) * board_size), 'black', 0.03, 'centre')

                            y_pos += 0.015
                            y_pos += line_spacing

                            for text in text_lines:
                                display_text(text, int(2.2675 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                                y_pos += 0.025
                                y_pos += line_spacing

            # Was that a strong move?
            if True:
                if state == 'transition to human player moved':
                    feedbacks[2] = None
                    selected_feedback_options[2] = False # this feedback option is not selected

                    # Draw a button for 'Was that a strong move?' feedback option
                    if True:
                        # Fill
                        pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                        # Top boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Bottom boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                        # Left boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                        # Right boundary
                        pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                        text = 'Was that a strong move?'
                        display_text(text, int(2.53125 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                elif state == 'human player moved':
                    if selected_feedback_options[2] == False: # if this option is not selected, draw the button again

                        # Draw a button for 'Was that a strong move?' feedback option
                        if True:
                            # Fill
                            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                            text = 'Was that a strong move?'
                            display_text(text, int(2.53125 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                    else:
                    
                        text_lines = feedbacks[2]
                    
                        window_height = 0.05 + 0.015 + line_spacing + (len(text_lines) * (0.025 + line_spacing)) + line_spacing
                    
                        # Draw a 'Why did {name} make this move?' feedback window
                        if True:
                            # Fill
                            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(window_height * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + window_height - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                    
                            y_pos += 0.05

                            text = 'Was that a strong move?'
                            display_text(text, int(2.53125 * board_size), int((y_pos) * board_size), 'black', 0.03, 'centre')

                            y_pos += 0.015
                            y_pos += line_spacing

                            for text in text_lines:
                                display_text(text, int(2.2675 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                                y_pos += 0.025
                                y_pos += line_spacing

                    y_pos += line_spacing
                    y_pos += line_spacing
                    y_pos += line_spacing
                    y_pos += line_spacing

            # What other move could I make?
            if state == 'human player moved':
                if selected_feedback_options[2] == True:
                    if what_other_move_could_i_make_first_appearance == True:
                        feedbacks[3] = None
                        selected_feedback_options[3] = False # this feedback option is not selected

                        what_other_move_could_i_make_y_pos = y_pos

                        # Draw a button for a feedback option
                        if True:
                            # Fill
                            pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                            # Top boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Bottom boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                            # Left boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                            # Right boundary
                            pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                            text = 'What other move could I make?'
                            display_text(text, int(2.53125 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                        what_other_move_could_i_make_first_appearance = False

                    else:
                        if selected_feedback_options[3] == False: # if this option is not selected, draw the button again

                            what_other_move_could_i_make_y_pos = y_pos

                            # Draw a button for a feedback option
                            if True:
                                # Fill
                                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                                # Top boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                                # Bottom boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + 0.092) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                                # Left boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                                # Right boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int(0.116 * board_size)])

                                text = 'What other move could I make?'
                                display_text(text, int(2.53125 * board_size), int((y_pos + 0.05) * board_size), 'black', 0.03, 'centre')

                        else:

                            text_lines = feedbacks[3]

                            window_height = 0.05 + 0.015 + line_spacing + (len(text_lines) * (0.025 + line_spacing)) + line_spacing
                    
                            what_other_move_could_i_make_y_pos = y_pos

                            # Draw a 'Why did {name} make this move?' feedback window
                            if True:
                                # Fill
                                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int((y_pos) * board_size), int(0.625 * board_size), int(window_height * board_size)])
                                # Top boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                                # Bottom boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos + window_height - 0.008) * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                                # Left boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                                # Right boundary
                                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int((y_pos - 0.008) * board_size), int(0.016 * board_size), int((window_height + 0.016) * board_size)])
                    
                                y_pos += 0.05

                                text = 'What other move could I make?'
                                display_text(text, int(2.53125 * board_size), int((y_pos) * board_size), 'black', 0.03, 'centre')

                                y_pos += 0.015
                                y_pos += line_spacing

                                for text in text_lines:
                                    display_text(text, int(2.2675 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                                    y_pos += 0.025
                                    y_pos += line_spacing

            # PASS THE MOVE OVER TO THE OPPONENT BUTTON
            if state in ['transition to human player moved', 'human player moved']:
                # Fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.21875 * board_size), int(1.22475 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not pass_the_move_over_to_the_opponent_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.21675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.31675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.22175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.32175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.84075 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Pass the move over to the opponent'
                display_text(text, int(2.53125 * board_size), int(1.27475 * board_size), 'black', 0.03, 'centre')

            return what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_exit_warning_window(board_size, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords, cancel_button_is_selected, exit_button_is_selected):

        try:

            line_spacing = 0.02

            # ERASE ALL TOP ROW BUTTONS / WHITE FILL
            if True:
                # Fills the left-top corner of the window with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(0.231 * board_size)])
                # Fills the right with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(0.231 * board_size)])

            # ERASE OTHER BUTTONS
            if True:
                # How are the points calculated? button
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.14825 * board_size), int((how_are_the_points_calculated_button_y_coords - 0.008) * board_size), int(0.641 * board_size), int(0.116 * board_size)])

                # Show the move history button
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.14825 * board_size), int((show_the_move_history_button_y_coords - 0.008) * board_size), int(0.641 * board_size), int(0.116 * board_size)])

            # ERASE FEEDBACK
            if True:
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.15 * board_size), int(0.365 * board_size), int(0.7625 * board_size), int(1.0285 * board_size)])

            # DRAW WARNING WINDOW (same size as the board)
            if True:
                # Feedback window fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(1 * board_size), int(0.356 * board_size), int(1 * board_size), int(1 * board_size)])
                # Feedback window top  
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(1 * board_size), int(0.356 * board_size), int(1 * board_size), int(0.015 * board_size)])
                # Feedback window bottom boundary
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(1 * board_size), int(1.341 * board_size), int(1 * board_size), int(0.015 * board_size)])
                # Feedback window left boundary
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(1 * board_size), int(0.356 * board_size), int(0.015 * board_size), int(1 * board_size)])
                # Feedback window right boundary
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(1.985 * board_size), int(0.356 * board_size), int(0.015 * board_size), int(1 * board_size)])
                # Fill - white 
                # Boundary - red

                y_pos = 0.435

                text = 'Warning'
                display_text(text, int(1.5 * board_size), int(y_pos * board_size), 'red', 0.08, 'centre')

                y_pos += 0.04
                y_pos += line_spacing
                y_pos += line_spacing

            # TEXT
            if True:
                text = 'Are you sure that you want to exit?'
                display_text(text, int(1.5 * board_size), int(0.55 * board_size), 'black', 0.04, 'centre')
                y_pos += 0.04
                y_pos += line_spacing

                text = 'If you exit now, this game will be lost'
                display_text(text, int(1.5 * board_size), int(0.62 * board_size), 'black', 0.04, 'centre')
                y_pos += 0.04
                y_pos += line_spacing

            # CANCEL BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.1 * board_size), int(1.156 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                if not cancel_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.092 * board_size), int(1.148 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.092 * board_size), int(1.248 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.092 * board_size), int(1.148 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.342 * board_size), int(1.148 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.097 * board_size), int(1.153 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.097 * board_size), int(1.253 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.097 * board_size), int(1.153 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.347 * board_size), int(1.153 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Cancel'
                display_text(text, int(1.225 * board_size), int(1.206 * board_size), 'black', 0.03, 'centre')

            # EXIT BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(1.65 * board_size), int(1.156 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                if not exit_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.642 * board_size), int(1.148 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.642 * board_size), int(1.248 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.642 * board_size), int(1.148 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.892 * board_size), int(1.148 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.647 * board_size), int(1.153 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.647 * board_size), int(1.253 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.647 * board_size), int(1.153 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(1.897 * board_size), int(1.153 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Exit'
                display_text(text, int(1.775 * board_size), int(1.206 * board_size), 'black', 0.03, 'centre')
    
        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_how_are_the_points_calculated_window(board_size, ok_button_is_selected):

        try:

            line_spacing = 0.02

            # ERASE ALL TOP ROW BUTTONS / WHITE FILL
            if True:
                # Fills the left-top corner of the window with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(0.231 * board_size)])
                # Fills the right with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(0.231 * board_size)])

            # ERASE FEEDBACK
            if True:
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.15 * board_size), int(0.365 * board_size), int(0.7625 * board_size), int(1.0285 * board_size)])

            # DRAW WARNING WINDOW (same size as the board)
            if True:
                # window fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.0625 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(1.1875 * board_size)])
                # window top  
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # window bottom boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(1.4035 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # window left boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # window right boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.86 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Fill - white
                # Boundary - light brown (same as on chess board)

                y_pos = 0.31

                text = 'How are the points'
                display_text(text, int(0.46875 * board_size), int(y_pos * board_size), 'dark brown', 0.08, 'centre')
                y_pos += 0.06
                y_pos += line_spacing

                text = 'calculated?'
                display_text(text, int(0.46875 * board_size), int(y_pos * board_size), 'dark brown', 0.08, 'centre')
                y_pos += 0.04
                y_pos += line_spacing

            # TEXT
            if True:
                text_sentences = ["The relative values of each of player's remaining pieces are added together."]
                text_sentences.append('The Queen is worth 100 points.')
                text_sentences.append('The Rook is worth 52.5 points.')
                text_sentences.append('The Bishop is worth 35 points.')
                text_sentences.append('The Knight is worth 35 points.')
                text_sentences.append('The Pawn is worth 10 points.')
                text_sentences.append('There are no points awarded for having a King, since it is impossible to capture the King without ending the game.')
                text_sentences.append(' ')
                text_sentences.append("Additional points are also added or subtracted for each piece. These points are based on the piece's strategic position and may change throughout the game. These points range from -5 to 5.")
                
                text_lines = []

                for sentence in text_sentences:
                    lines = split_text_into_lines(sentence, 0.7125)
                    for line in lines:
                        text_lines.append(line)

                for text in text_lines:

                    display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.025, 'left')
                    y_pos += 0.025
                    y_pos += line_spacing

            # OK BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.36875 * board_size), int(1.261875 * board_size), int(0.20 * board_size), int(0.10 * board_size)])
                if not ok_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36075 * board_size), int(1.2538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36075 * board_size), int(1.3538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36075 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.56075 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36575 * board_size), int(1.258875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36575 * board_size), int(1.358875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36575 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.56575 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'OK'
                display_text(text, int(0.46875 * board_size), int(1.311875 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_move_history_window(board_size, written_move_history_page, previous_page_button_is_selected, next_page_button_is_selected, exit_button_is_selected):
        
        try:

            line_spacing = 0.02

            # ERASE ALL TOP ROW BUTTONS / WHITE FILL
            if True:
                # Fills the left-top corner of the window with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(0.231 * board_size)])
                # Fills the right with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(0.231 * board_size)])

            # ERASE FEEDBACK
            if True:
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.15 * board_size), int(0.365 * board_size), int(0.7625 * board_size), int(1.0285 * board_size)])

            # DRAW THE MOVE HISTORY WINDOW (Overfill the game statistics window, white fill)
            if True:
                # window fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.0625 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(1.1875 * board_size)])
                # window top  
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # window bottom boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(1.4035 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # window left boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.0625 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # window right boundary
                pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.86 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Fill - white
                # Boundary - light brown (same as on chess board)

                y_pos = 0.31

                text = 'Move history'
                display_text(text, int(0.46875 * board_size), int(y_pos * board_size), 'dark brown', 0.08, 'centre')

                y_pos += 0.04
                y_pos += line_spacing

            # Display move history
            if True:

                for move_pair in written_move_history_page:
                    text = ('{}. '.format(move_pair[0]))
                    display_text(text, int(0.1125 * board_size), int(y_pos * board_size), 'black', 0.03, 'left')

                    for text_line in move_pair[1]:
                        display_text(text_line, int(0.1425 * board_size), int(y_pos * board_size), 'black', 0.03, 'left') # width = 0.5875
                        y_pos += 0.03
                        y_pos += line_spacing

                    if len(move_pair) == 3:
                        for text_line in move_pair[2]:
                            display_text(text_line, int(0.1425 * board_size), int(y_pos * board_size), 'black', 0.03, 'left') # width = 0.5875
                            y_pos += 0.03
                            y_pos += line_spacing

            # Previous page BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.119125 * board_size), int(1.261875 * board_size), int(0.20 * board_size), int(0.10 * board_size)])
                if not previous_page_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.111125 * board_size), int(1.2538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.111125 * board_size), int(1.3538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.111125 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.311125 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.116125 * board_size), int(1.258875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.116125 * board_size), int(1.358875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.116125 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.316125 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Previous page'
                display_text(text, int(0.219125 * board_size), int(1.311875 * board_size), 'black', 0.03, 'centre')

            # Next page BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.36875 * board_size), int(1.261875 * board_size), int(0.20 * board_size), int(0.10 * board_size)])
                if not next_page_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36075 * board_size), int(1.2538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36075 * board_size), int(1.3538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36075 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.56075 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36575 * board_size), int(1.258875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36575 * board_size), int(1.358875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.36575 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.56575 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Next page'
                display_text(text, int(0.46875 * board_size), int(1.311875 * board_size), 'black', 0.03, 'centre')

            # Exit BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.618375 * board_size), int(1.261875 * board_size), int(0.20 * board_size), int(0.10 * board_size)])
                if not exit_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.610375 * board_size), int(1.2538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.610375 * board_size), int(1.3538875 * board_size), int(0.216 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.610375 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.810375 * board_size), int(1.2538875 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.615375 * board_size), int(1.258875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.615375 * board_size), int(1.358875 * board_size), int(0.206 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.615375 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(0.815375 * board_size), int(1.258875 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'OK'
                display_text(text, int(0.718375 * board_size), int(1.311875 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def refresh_print_game_over_window(board_size, game_outcome, player, current_color, move_counter, average_time_per_move_white, average_time_per_move_black, how_undo_button, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords, ok_button_is_selected, undo_a_move_button_is_selected, show_undo_button, continue_button_is_visible, continue_button_is_selected):

        try:

            line_spacing = 0.015

            # ERASE ALL TOP ROW BUTTONS / WHITE FILL
            if True:
                # Fills the left-top corner of the window with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [0, 0, int(0.875 * board_size), int(0.231 * board_size)])
                # Fills the right with white to erase previous contents
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), 0, int(0.875 * board_size), int(0.231 * board_size)])

            # ERASE OTHER BUTTONS
            if True:
                # How are the points calculated? button
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.14825 * board_size), int((how_are_the_points_calculated_button_y_coords - 0.008) * board_size), int(0.641 * board_size), int(0.116 * board_size)])

                # Show the move history button
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(0.14825 * board_size), int((show_the_move_history_button_y_coords - 0.008) * board_size), int(0.641 * board_size), int(0.116 * board_size)])

            # DRAW GAME OVER WINDOW
            if True:
                # Feedback window fill
                pygame.draw.rect(gameDisplay, (255, 255, 255), [int(2.125 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(1.1875 * board_size)])
                # Feedback window top  
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(2.125 * board_size), int(0.231 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # Feedback window bottom boundary
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(2.125 * board_size), int(1.4035 * board_size), int(0.8125 * board_size), int(0.015 * board_size)])
                # Feedback window left boundary
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(2.125 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Feedback window right boundary
                pygame.draw.rect(gameDisplay, (255, 0, 0), [int(2.9225 * board_size), int(0.231 * board_size), int(0.015 * board_size), int(1.1875 * board_size)])
                # Fill - dark brown (same as on chess board)
                # Boundary - light brown (same as on chess board)

                y_pos = 0.31

                if game_outcome in [-1, 1]:
                    text = 'Checkmate'
                elif game_outcome == 2:
                    text = 'Stalemate'
                elif game_outcome == 3:
                    text = 'Draw'
                elif game_outcome == 4:
                    text = 'Forfeit'
                elif game_outcome == 5:
                    text = 'You ran out of time!'

                display_text(text, int(2.53125 * board_size), int(y_pos * board_size), 'red', 0.08, 'centre')

                y_pos += 0.04
                y_pos += line_spacing
                y_pos += line_spacing
                y_pos += line_spacing
            
            # Write game statistics
            if True:

                # Who won?
                if game_outcome in [-1, 1, 4, 5]:
                    text = ('{} won.'.format(player[not current_color]))
                    #display_text(text, int(2.175 * board_size), int(y_pos * board_size), 'black', 0.035, 'left')
                    display_text(text, int(2.53125 * board_size), int(y_pos * board_size), 'black', 0.035, 'centre')
                    y_pos += 0.035
                    y_pos += line_spacing

                # Average time per move
                text = ('Average time per move:')
                display_text(text, int(2.175 * board_size), int(y_pos * board_size), 'black', 0.035, 'left')
                y_pos += 0.035
                y_pos += line_spacing

                if not player[True] == 'Computer':

                    if not average_time_per_move_white == None:
                        if not average_time_per_move_white // 60 == 0:
                            text = ('{} - {}min {}s'.format(player[True], int(average_time_per_move_white // 60), round(average_time_per_move_white % 60), 1)) # Display as minutes + seconds
                        else:
                            text = ('{} - {}s'.format(player[True], average_time_per_move_white)) # Display as seconds only
                        display_text(text, int(2.175 * board_size), int(y_pos * board_size), 'black', 0.03, 'left')
                        y_pos += 0.03
                        y_pos += line_spacing

                if not player[False] == 'Computer':

                    if not average_time_per_move_black == None:
                        if not average_time_per_move_black // 60 == 0:
                            text = ('{} - {}min {}s'.format(player[False], int(average_time_per_move_black // 60), round(average_time_per_move_black % 60), 1)) # Display as minutes + seconds
                        else:
                            text = ('{} - {}s'.format(player[False], average_time_per_move_black)) # Display as seconds only
                        display_text(text, int(2.175 * board_size), int(y_pos * board_size), 'black', 0.03, 'left')
                        y_pos += 0.03
                        y_pos += line_spacing

                # Total number of moves:
                if current_color == True:
                    text = ('Total number of moves: {}'.format(move_counter - 1))
                else:
                    text = ('Total number of moves: {}'.format(move_counter))

                display_text(text, int(2.175 * board_size), int(y_pos * board_size), 'black', 0.035, 'left')
                y_pos += 0.035
                y_pos += line_spacing

            # UNDO TWO MOVES BUTTON
            if show_undo_button:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.625 * board_size), int(0.0655 * board_size), int(0.25 * board_size), int(0.10 * board_size)])
                if not undo_a_move_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.617 * board_size), int(0.0575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.617 * board_size), int(0.1575 * board_size), int(0.266 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.617 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.867 * board_size), int(0.0575 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.622 * board_size), int(0.0625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.622 * board_size), int(0.1625 * board_size), int(0.256 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.622 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.872 * board_size), int(0.0625 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Undo two moves'
                display_text(text, int(2.75 * board_size), int(0.1155 * board_size), 'black', 0.03, 'centre')

            # CONTINUE BUTTON
            if continue_button_is_visible:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.21875 * board_size), int(1.07475 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not continue_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.06675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.16675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.06675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int(1.06675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.07175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.17175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.07175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.84075 * board_size), int(1.07175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Continue the game. Random move will be made for you.'
                display_text(text, int(2.53125 * board_size), int(1.12475 * board_size), 'black', 0.03, 'centre')

            # OK BUTTON
            if True:
                # Fill
                pygame.draw.rect(gameDisplay, (252, 221, 174), [int(2.21875 * board_size), int(1.22475 * board_size), int(0.625 * board_size), int(0.10 * board_size)])
                if not ok_button_is_selected:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.21675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.31675 * board_size), int(0.633 * board_size), int(0.016 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21075 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.83575 * board_size), int(1.21675 * board_size), int(0.016 * board_size), int(0.116 * board_size)])
                else:
                    # Top boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.22175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Bottom boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.32175 * board_size), int(0.631 * board_size), int(0.006 * board_size)])
                    # Left boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.21757 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])
                    # Right boundary
                    pygame.draw.rect(gameDisplay, (177, 82, 25), [int(2.84075 * board_size), int(1.22175 * board_size), int(0.006 * board_size), int(0.106 * board_size)])

                text = 'Go back to menu'
                display_text(text, int(2.53125 * board_size), int(1.27475 * board_size), 'black', 0.03, 'centre')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # GUI visualisation

if True:
    def setup_human_vs_computer(board_size):

        try:

            go_back = None
            selected_color = 'white'
            selected_time_limit = 'unlimited'
            selected_cheat_limit = 'unlimited'
            selected_name = automatically_select_a_name(None)
            go_back_button_is_selected = False
            go_to_game_button_is_selected = False
            new_name_is_visible = False
            delete_selected_name_right_button_is_selected = False
            delete_selected_name_button_is_visible = False
            cheat_counter_white = 0
            cheat_counter_black = 0

            # Frame loop
            while True:
            
                list_of_names = get_list_of_names()
                if len(list_of_names) > 10:
                    new_name_is_visible = False
                else:
                    new_name_is_visible = True

                if selected_name == 'New name' and new_name_is_visible: # Register new name
                    selected_name = new_name_input_window(board_size)
                    add_new_name(selected_name)

                if selected_name == 'Play as a guest' or len(list_of_names) == 4: # If Play as a Guest is selected or only 2 names are registered
                    delete_selected_name_button_is_visible = False
                else:
                    delete_selected_name_button_is_visible = True

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(1.125 * board_size) < x_coord < int(1.375 * board_size) and int(0.35 * board_size) < y_coord < int(0.45 * board_size):
                            selected_color = 'white'
                        elif int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(0.35 * board_size) < y_coord < int(0.45 * board_size):
                            selected_color = 'black'
                        elif int(1.625 * board_size) < x_coord < int(1.875 * board_size) and int(0.35 * board_size) < y_coord < int(0.45 * board_size):
                            selected_color = 'random'
                        elif int(0.875 * board_size) < x_coord < int(1.125 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = 'unlimited'
                        elif int(1.125 * board_size) < x_coord < int(1.375 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '10 seconds'
                        elif int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '30 seconds'
                        elif int(1.625 * board_size) < x_coord < int(1.875 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '1 minute'
                        elif int(1.875 * board_size) < x_coord < int(2.125 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '2 minutes'
                        elif int(0.875 * board_size) < x_coord < int(1.125 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = 'unlimited'
                        elif int(1.125 * board_size) < x_coord < int(1.375 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = 'no cheats'
                        elif int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = '5 cheats'
                        elif int(1.625 * board_size) < x_coord < int(1.875 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = '10 cheats'
                        elif int(1.875 * board_size) < x_coord < int(2.125 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = '20 cheats'
                        elif int(0.875 * board_size) < x_coord < int(1.125 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                            go_back_button_is_selected = True
                        elif int(1.875 * board_size) < x_coord < int(2.125 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                            go_to_game_button_is_selected = True
                        elif int(2.3125 * board_size) < x_coord < int(2.8125 * board_size) and int(0.131 * board_size) < y_coord < int(0.231 * board_size) and delete_selected_name_button_is_visible:
                            delete_selected_name_right_button_is_selected = True

                        list_of_names_copy = list_of_names[:]
                        if not new_name_is_visible:
                            list_of_names_copy.remove('New name')

                        difference = 0
                        for name in list_of_names_copy:
                            if int(2.25 * board_size) < x_coord < int(2.875 * board_size) and int((0.35 + difference) * board_size) < y_coord < int((0.45 + difference) * board_size):
                                selected_name = name
                            difference += 0.1

                    elif go_back_button_is_selected or go_to_game_button_is_selected:

                        board, castling_info, current_color, _ = get_a_game_scenario('Classic')

                        if go_back_button_is_selected:
                        
                            go_back = True
                            player = None
                            time_limit = None
                            cheat_limit = None

                        elif go_to_game_button_is_selected:

                            if selected_name == 'Play as a guest':
                                name = 'Human'
                            else:
                                name = selected_name

                            go_back = False

                            if selected_color == 'white':
                                player = {True: name,
                                          False: 'Computer'}
                            elif selected_color == 'black':
                                player = {True: 'Computer',
                                          False: name}
                            else: # selected_color == 'random'
                                if random.randint(0,1) == 0:
                                    player = {True: name,
                                              False: 'Computer'}
                                else:
                                    player = {True: 'Computer',
                                              False: name}

                            if selected_time_limit == 'unlimited':
                                time_limit = None
                            elif selected_time_limit == '10 seconds':
                                time_limit = 10
                            elif selected_time_limit == '30 seconds':
                                time_limit = 30
                            elif selected_time_limit == '1 minute':
                                time_limit = 60
                            else: # selected_time_limit == '2 minutes'
                                time_limit = 120

                            if selected_cheat_limit == 'unlimited':
                                cheat_limit = None
                            elif selected_cheat_limit == 'no cheats':
                                cheat_limit = 0
                            elif selected_cheat_limit == '5 cheats':
                                cheat_limit = 5
                            elif selected_cheat_limit == '10 cheats':
                                cheat_limit = 10
                            else: # selected_cheat_limit == '20 cheats'
                                cheat_limit = 20

                        return go_back, board, castling_info, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black

                    elif delete_selected_name_right_button_is_selected and delete_selected_name_button_is_visible:
                        delete_selected_name_right_button_is_selected = False
                        delete_name(selected_name)
                        selected_name = automatically_select_a_name(None)

                refresh_print_setup_window_human_vs_computer(board_size, selected_color, selected_time_limit, selected_cheat_limit, go_back_button_is_selected, go_to_game_button_is_selected, selected_name, new_name_is_visible, delete_selected_name_right_button_is_selected, delete_selected_name_button_is_visible)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def setup_human_vs_human(board_size):

        try:

            selected_time_limit = 'unlimited'
            selected_cheat_limit = 'unlimited'
            selected_name_white_player = automatically_select_a_name(None)
            selected_name_black_player = automatically_select_a_name(selected_name_white_player)
            go_back_button_is_selected = False
            go_to_game_button_is_selected = False
            new_name_is_visible = False
            delete_selected_name_right_button_is_selected = False
            delete_selected_name_left_button_is_selected = False
            delete_selected_name_button_is_visible = False
            cheat_counter_white = 0
            cheat_counter_black = 0

            # Frame loop
            while True:

                list_of_names = get_list_of_names()
                if len(list_of_names) > 10:
                    new_name_is_visible = False
                else:
                    new_name_is_visible = True

                if selected_name_white_player == 'New name' and new_name_is_visible: # Register new name (White player)
                    selected_name_white_player = new_name_input_window(board_size)
                    add_new_name(selected_name_white_player)

                if selected_name_black_player == 'New name' and new_name_is_visible: # Register new name (Black player)
                    selected_name_black_player = new_name_input_window(board_size)
                    add_new_name(selected_name_black_player)

                if len(list_of_names) == 4: # If only 2 names are registered
                    delete_selected_name_button_is_visible = False
                else:
                    delete_selected_name_button_is_visible = True

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(0.875 * board_size) < x_coord < int(1.125 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = 'unlimited'
                        elif int(1.125 * board_size) < x_coord < int(1.375 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '10 seconds'
                        elif int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '30 seconds'
                        elif int(1.625 * board_size) < x_coord < int(1.875 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '1 minute'
                        elif int(1.875 * board_size) < x_coord < int(2.125 * board_size) and int(0.6565 * board_size) < y_coord < int(0.7565 * board_size):
                            selected_time_limit = '2 minutes'
                        elif int(0.875 * board_size) < x_coord < int(1.125 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = 'unlimited'
                        elif int(1.125 * board_size) < x_coord < int(1.375 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = 'no cheats'
                        elif int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = '5 cheats'
                        elif int(1.625 * board_size) < x_coord < int(1.875 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = '10 cheats'
                        elif int(1.875 * board_size) < x_coord < int(2.125 * board_size) and int(0.963 * board_size) < y_coord < int(1.063 * board_size):
                            selected_cheat_limit = '20 cheats'
                        elif int(0.875 * board_size) < x_coord < int(1.125 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                            go_back_button_is_selected = True
                        elif int(1.875 * board_size) < x_coord < int(2.125 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                            go_to_game_button_is_selected = True
                        elif int(2.3125 * board_size) < x_coord < int(2.8125 * board_size) and int(0.131 * board_size) < y_coord < int(0.231 * board_size) and delete_selected_name_button_is_visible:
                            delete_selected_name_right_button_is_selected = True
                        elif int(0.1875 * board_size) < x_coord < int(0.6875 * board_size) and int(0.131 * board_size) < y_coord < int(0.231 * board_size) and delete_selected_name_button_is_visible:
                            delete_selected_name_left_button_is_selected = True

                        list_of_names_copy = list_of_names[:]
                        if not new_name_is_visible:
                            list_of_names_copy.remove('New name')

                        # Name selection - WHITE
                        difference = 0
                        for name in list_of_names_copy:
                            if not name == 'Play as a guest':
                                if int(0.125 * board_size) < x_coord < int(0.75 * board_size) and int((0.35 + difference) * board_size) < y_coord < int((0.45 + difference) * board_size) and not name == selected_name_black_player:
                                    selected_name_white_player = name
                                difference += 0.1

                        # Name selection - BLACK
                        difference = 0
                        for name in list_of_names_copy:
                            if not name == 'Play as a guest':
                                if int(2.25 * board_size) < x_coord < int(2.875 * board_size) and int((0.35 + difference) * board_size) < y_coord < int((0.45 + difference) * board_size) and not name == selected_name_white_player:
                                    selected_name_black_player = name
                                difference += 0.1

                    elif go_back_button_is_selected or go_to_game_button_is_selected:

                        board, castling_info, current_color, _ = get_a_game_scenario('Classic')

                        if go_back_button_is_selected:
                        
                            go_back = True
                            player = None
                            time_limit = None
                            cheat_limit = None

                        elif go_to_game_button_is_selected:

                            go_back = False

                            player = {True: selected_name_white_player,
                                      False: selected_name_black_player}

                            if selected_time_limit == 'unlimited':
                                time_limit = None
                            elif selected_time_limit == '10 seconds':
                                time_limit = 10
                            elif selected_time_limit == '30 seconds':
                                time_limit = 30
                            elif selected_time_limit == '1 minute':
                                time_limit = 60
                            else: # selected_time_limit == '2 minutes'
                                time_limit = 120

                            if selected_cheat_limit == 'unlimited':
                                cheat_limit = None
                            elif selected_cheat_limit == 'no cheats':
                                cheat_limit = 0
                            elif selected_cheat_limit == '5 cheats':
                                cheat_limit = 5
                            elif selected_cheat_limit == '10 cheats':
                                cheat_limit = 10
                            else: # selected_cheat_limit == '20 cheats'
                                cheat_limit = 20

                        return go_back, board, castling_info, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black

                    elif delete_selected_name_right_button_is_selected and delete_selected_name_button_is_visible: # Delete Black's selected name
                        delete_selected_name_right_button_is_selected = False
                        delete_name(selected_name_black_player)
                        selected_name_black_player = automatically_select_a_name(None)
                        selected_name_white_player = automatically_select_a_name(selected_name_black_player)

                    elif delete_selected_name_left_button_is_selected and delete_selected_name_button_is_visible: # Delete White's selected name
                        delete_selected_name_left_button_is_selected = False
                        delete_name(selected_name_white_player)
                        selected_name_white_player = automatically_select_a_name(None)
                        selected_name_black_player = automatically_select_a_name(selected_name_white_player)

                refresh_print_setup_window_human_vs_human(board_size, selected_time_limit, selected_cheat_limit, go_back_button_is_selected, go_to_game_button_is_selected, selected_name_white_player, selected_name_black_player, delete_selected_name_right_button_is_selected, delete_selected_name_left_button_is_selected, delete_selected_name_button_is_visible, new_name_is_visible)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def scenario_selection_window(board_size):

        try:

            selected_scenario = 0 # 'Classic'
            go_back_button_is_selected = False
            delete_button_is_selected = False
            create_new_scenario_button_is_selected = False
            go_to_game_button_is_selected = False
            delete_button_is_visible = False
            create_new_scenario_button_is_visible = False

            # Frame loop
            while True:

                game_scenarios = get_game_scenarios()

                if len(game_scenarios) > 7:
                    create_new_scenario_button_is_visible = False
                else:
                    create_new_scenario_button_is_visible = True

                if selected_scenario == 0:
                    delete_button_is_visible = False
                else:
                    delete_button_is_visible = True

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(0.875 * board_size) < x_coord < int(1.125 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                           go_back_button_is_selected = True
                        elif int(1.20833 * board_size) < x_coord < int(1.45833 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size) and delete_button_is_visible:
                           delete_button_is_selected = True
                        elif int(1.54167 * board_size) < x_coord < int(1.79167 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size) and create_new_scenario_button_is_visible:
                           create_new_scenario_button_is_selected = True
                        elif int(1.875 * board_size) < x_coord < int(2.125 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                           go_to_game_button_is_selected = True

                        difference = 0
                        for index in range(len(game_scenarios)):
                            if int(1.1875 * board_size) < x_coord < int(1.8125 * board_size) and int((0.35 + difference) * board_size) < y_coord < int((0.45 + difference) * board_size):
                                selected_scenario = index
                            difference += 0.1

                    elif delete_button_is_selected and delete_button_is_visible:
                        delete_button_is_selected = False
                        delete_a_game_scenario(selected_scenario)
                        selected_scenario = 0 # 'Classic'
                    
                    elif create_new_scenario_button_is_selected and create_new_scenario_button_is_visible:
                        create_new_scenario_button_is_selected = False

                        decision = 'Create scenario'

                        board = []
                        for _ in range(64): # Fill board with blanks
                            board.append('-')
                        board[4] = 'K'
                        board[60] = 'k' # Place the kings

                        castling_info = game_scenarios[0][2]
                        player = game_scenarios[selected_scenario][4]
                        current_color = game_scenarios[selected_scenario][3]
                        time_limit = None
                        cheat_limit = None
                        cheat_counter_white = 0
                        cheat_counter_black = 0

                        return decision, board, castling_info, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black
                    
                    elif go_back_button_is_selected or go_to_game_button_is_selected:

                        if go_back_button_is_selected:

                            board, castling_info, current_color, _ = get_a_game_scenario('Classic')

                            decision = 'Go back'
                            player = None
                            time_limit = None
                            cheat_limit = None
                            cheat_counter_white = None
                            cheat_counter_black = None
                        else:
                            decision = 'Play'
                            board = game_scenarios[selected_scenario][1]
                            castling_info = game_scenarios[selected_scenario][2]
                            player = game_scenarios[selected_scenario][4]
                            current_color = game_scenarios[selected_scenario][3]
                            time_limit = None
                            cheat_limit = None
                            cheat_counter_white = 0
                            cheat_counter_black = 0

                        return decision, board, castling_info, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black

                refresh_print_scenario_selection_window(board_size, selected_scenario, delete_button_is_selected, create_new_scenario_button_is_selected, go_back_button_is_selected, go_to_game_button_is_selected, delete_button_is_visible, create_new_scenario_button_is_visible)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def game_history_window(board_size):

        try:

            go_back_button_is_selected = False

            table_y_coord = 0.23

            game_history = get_structured_game_history()

            # Frame loop
            while True:

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                           go_back_button_is_selected = True

                        for n, item in enumerate(game_history):
                            if int(2.2625 * board_size) < x_coord < int(2.5625 * board_size) and int(((table_y_coord + 0.1) + n * 0.1) * board_size) < y_coord < int(((table_y_coord + 0.2) + n * 0.1) * board_size):
                               list_of_games_window(board_size, item[0])

                    elif go_back_button_is_selected:
                        go_back_button_is_selected = False

                        # Fills a small bar on top above the logo (to erase a small part of the game history table)
                        pygame.draw.rect(gameDisplay, (255, 255, 255), [int(0.875 * board_size), int(0.2 * board_size), int(1.25 * board_size), int(0.031 * board_size)])

                        return

                refresh_print_game_history_window(board_size, go_back_button_is_selected, game_history, table_y_coord)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def list_of_games_window(board_size, player_name):

        try:

            go_back_button_is_selected = False
            previous_page_button_is_selected = False
            next_page_button_is_selected = False
            selected_page_no = 0

            list_of_games_pages = get_list_of_games(player_name)

            # Frame loop
            while True:

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(1.025 * board_size) < x_coord < int(1.275 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                           previous_page_button_is_selected = True
                        elif int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                           next_page_button_is_selected = True
                        elif int(1.725 * board_size) < x_coord < int(1.975 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size):
                           go_back_button_is_selected = True

                    elif previous_page_button_is_selected:
                        previous_page_button_is_selected = False
                        if not selected_page_no == 0:
                            selected_page_no -= 1

                    elif next_page_button_is_selected:
                        next_page_button_is_selected = False
                        if not selected_page_no == len(list_of_games_pages) - 1:
                            selected_page_no += 1

                    elif go_back_button_is_selected:
                        go_back_button_is_selected = False
                        return

                refresh_print_list_of_games_window(board_size, go_back_button_is_selected, previous_page_button_is_selected, next_page_button_is_selected, player_name, selected_page_no, list_of_games_pages)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def scenario_name_input_window(board_size):

        try:

            ok_button_is_selected = False
            ok_button_is_visible = False

            textinput = TextInput(initial_string="New scenario", font_size=int(0.05 * board_size))

            # Frame loop
            while True:

                if textinput.get_text() in ['', 'Classic']:
                    ok_button_is_visible = False
                else:
                    ok_button_is_visible = True

                # Detects events through pygame and goes through them
                events = pygame.event.get()
                for event in events:

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size) and ok_button_is_visible:
                            ok_button_is_selected = True

                    elif ok_button_is_selected and ok_button_is_visible:
                        ok_button_is_selected = False
                        return textinput.get_text()

                # Feed it with events every frame
                textinput.update(events)
                refresh_print_scenario_name_input_window(board_size, ok_button_is_selected, ok_button_is_visible, textinput)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def new_name_input_window(board_size):

        try:

            ok_button_is_selected = False
            ok_button_is_visible = False

            textinput = TextInput(initial_string="", font_size=int(0.05 * board_size))

            # Frame loop
            while True:

                list_of_names = get_list_of_names()

                if textinput.get_text() in list_of_names or textinput.get_text() in ['', 'Computer']:
                    ok_button_is_visible = False
                else:
                    ok_button_is_visible = True

                # Detects events through pygame and goes through them
                events = pygame.event.get()
                for event in events:

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(1.375 * board_size) < x_coord < int(1.625 * board_size) and int(1.2695 * board_size) < y_coord < int(1.3695 * board_size) and ok_button_is_visible:
                            ok_button_is_selected = True

                    elif ok_button_is_selected and ok_button_is_visible:
                        ok_button_is_selected = False
                        return textinput.get_text()

                # Feed it with events every frame
                textinput.update(events)
                refresh_print_new_name_input_window(board_size, ok_button_is_selected, ok_button_is_visible, textinput)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def exit_warning_window(board_size, how_are_the_points_calculated_button_y_coords):

        try:

            cancel_button_is_selected = False
            exit_button_is_selected = False

            # Frame loop
            while True:

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(1.1 * board_size) < x_coord < int(1.35 * board_size) and int(1.156 * board_size) < y_coord < int(1.256 * board_size):
                           cancel_button_is_selected = True
                        elif int(1.65 * board_size) < x_coord < int(1.9 * board_size) and int(1.156 * board_size) < y_coord < int(1.256 * board_size):
                           exit_button_is_selected = True


                    elif cancel_button_is_selected:
                        cancel_button_is_selected = False
                        return True # cancel = True
                
                    elif exit_button_is_selected:
                        exit_button_is_selected = False
                        return False # cancel = False

                refresh_print_exit_warning_window(board_size, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords, cancel_button_is_selected, exit_button_is_selected)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def how_are_the_points_calculated_window(board_size, how_are_the_points_calculated_button_y_coords):
        
        try:

            ok_button_is_selected = False

            # Frame loop
            while True:

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(0.36875 * board_size) < x_coord < int(0.56875 * board_size) and int(1.261875 * board_size) < y_coord < int(1.361875 * board_size):
                           ok_button_is_selected = True

                    elif ok_button_is_selected:
                        ok_button_is_selected = False
                        return
                
                refresh_print_how_are_the_points_calculated_window(board_size, ok_button_is_selected)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def move_history_window(board_size, state, player, current_color, move_history):

        try:

            previous_page_button_is_selected = False
            next_page_button_is_selected = False
            exit_button_is_selected = False

            current_page_index = 0

            written_move_history_array = create_written_move_history_array(state, player, move_history)

            # Frame loop
            while True:

                if not written_move_history_array == []:
                    written_move_history_page = written_move_history_array[current_page_index]
                else:
                    written_move_history_page = []

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(0.119125 * board_size) < x_coord < int(0.319125 * board_size) and int(1.261875 * board_size) < y_coord < int(1.361875 * board_size):
                           previous_page_button_is_selected = True
                        elif int(0.36875 * board_size) < x_coord < int(0.56875 * board_size) and int(1.261875 * board_size) < y_coord < int(1.361875 * board_size):
                           next_page_button_is_selected = True
                        elif int(0.618375 * board_size) < x_coord < int(0.818375 * board_size) and int(1.261875 * board_size) < y_coord < int(1.361875 * board_size):
                           exit_button_is_selected = True

                    elif previous_page_button_is_selected:
                        previous_page_button_is_selected = False
                        if not current_page_index == 0:
                            current_page_index -= 1

                    elif next_page_button_is_selected:
                        next_page_button_is_selected = False
                        if not current_page_index == (len(written_move_history_array) - 1):
                            current_page_index += 1

                    elif exit_button_is_selected:
                        exit_button_is_selected = False
                        return

                refresh_print_move_history_window(board_size, written_move_history_page, previous_page_button_is_selected, next_page_button_is_selected, exit_button_is_selected)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def game_over_window(game_outcome, player, move_counter, average_time_per_move_white, average_time_per_move_black, show_undo_button, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords):
        
        try:

            ok_button_is_selected = False
            undo_a_move_button_is_selected = False
            continue_button_is_selected = False

            if game_outcome == 5:
                continue_button_is_visible = True
            else:
                continue_button_is_visible = False

            # Frame loop
            while True:

                # Detects events through pygame and goes through them
                for event in pygame.event.get():

                    if event.type == pygame.QUIT: # Detects if the top-right cross was clicked
                        quit_program() # Quits the program

                    elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                        mouse_coords = pygame.mouse.get_pos()
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if int(2.21875 * board_size) < x_coord < int(2.84375 * board_size) and int(1.22475 * board_size) < y_coord < int(1.361875 * board_size):
                           ok_button_is_selected = True
                        elif show_undo_button and int(2.625 * board_size) < x_coord < int(2.875 * board_size) and int(0.0655 * board_size) < y_coord < int(0.1655 * board_size):
                           undo_a_move_button_is_selected = True
                        elif continue_button_is_visible and int(2.21875 * board_size) < x_coord < int(2.84375 * board_size) and int(1.07475 * board_size) < y_coord < int(1.17475 * board_size):
                           continue_button_is_selected = True

                    elif ok_button_is_selected:
                        ok_button_is_selected = False

                        add_game_result_to_game_history(player[not current_color], player[current_color], game_outcome)
                        alter_average_times_per_move(player, average_time_per_move_white, average_time_per_move_black)

                        return False # undo = False

                    elif undo_a_move_button_is_selected:
                        undo_a_move_button_is_selected = False
                        return True # undo = True

                    elif continue_button_is_selected:
                        continue_button_is_selected = False
                        return True # continue = True
                
                refresh_print_game_over_window(board_size, game_outcome, player, current_color, move_counter, average_time_per_move_white, average_time_per_move_black, show_undo_button, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords, ok_button_is_selected, undo_a_move_button_is_selected, show_undo_button, continue_button_is_visible, continue_button_is_selected)

                # Keeps the frames running
                pygame.display.update()
                clock.tick(60)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # Internal frame loops

if True:
    def create_written_move_history_array(state, player, move_history):

        try:

            # [page1, page2, page3, ...]
            #
            # [[[move_no, [white move line1], [black move line1, black move line2]], [move_no, [white move line 1], [black move line 1]], ...], [another page], ...]
    
            max_number_of_lines = 17 - 1 # it is actually 17, but it only seems to work when set to 16
            color = True
            written_move_history_array = []

            # Writes sentences
            for move in move_history:
                sentence = player[color] + ' ' + write_move(move, tense = 'past', lower_case = False)
                written_move_history_array.append(sentence)
                color = not color

            # Splits sentences into lines
            for index, sentence in enumerate(written_move_history_array):
                text_lines = split_text_into_lines(sentence, 0.5575)
                written_move_history_array[index] = text_lines

            # Combines a White move with the following Black move
            if True:
                n = 1
                new_written_move_history_array = []
                for index, sentence in enumerate(written_move_history_array):

                    if index % 2 == 0:
                        new_written_move_history_array.append([n, sentence])
                        n += 1
                    else:
                        new_written_move_history_array[-1].append(sentence)

                written_move_history_array = deepcopy(new_written_move_history_array)

            # Splits into multiple pages
            if True:

                page_first_indexes = [0]
                new_written_move_history_array = []
                lines = 0

                for index, move_pair in enumerate(written_move_history_array):

                    if len(move_pair) == 3:
                        lines += (len(move_pair[1]) + len(move_pair[2]))
                    else:
                        lines += len(move_pair[1])

                    if lines >= max_number_of_lines or index == (len(written_move_history_array) - 1):
                        first_index = page_first_indexes[-1]
                        lines = 0
                        if lines > max_number_of_lines:
                            last_index = index - 1
                            page_first_indexes.append(index)
                        else:
                            last_index = index
                            page_first_indexes.append(index + 1)

                        new_written_move_history_array.append(written_move_history_array[first_index:(last_index + 1)])

                written_move_history_array = deepcopy(new_written_move_history_array)

            return written_move_history_array

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def split_text_into_lines(sentence, line_length_in_unit_pixels):

        try:

            # Characted density is about 100 characters per unit pixel
            # length in actual pixels = int((length in unit pixels) * board_size)

            text_lines = []
            characters_per_line = int(100 * line_length_in_unit_pixels)

            while True:

                if 0 < len(sentence) <= characters_per_line:
                    text_lines.append(sentence)
                    return text_lines
                elif len(sentence) == 0:
                    return text_lines
                else:

                    pos = characters_per_line

                    while True:
                        if sentence[pos] == ' ':
                            text_lines.append(sentence[:pos])
                            sentence = sentence[(pos + 1):] # Delete the characters before the space
                            break
                        pos -= 1

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def write_move_with_prefix(state, player, move_history):

        try:

            last_move = move_history[-1]

            sentence = ''

            if len(move_history) % 2 == 1:
                opponent_name = player[True]
            else:
                opponent_name = player[False]

            if state in ['transition to human player moved', 'human player moved']:
                sentence += 'You '
            else:
                sentence += ('Last move: {} '.format(opponent_name))

            sentence += write_move(last_move, tense = 'past', lower_case = True)

            return sentence

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def write_move(move, tense, lower_case):

        # tenses:
        # 'past' - moved
        # 'present' - move
        # 'present progressive' - moving

        try:

            sentence = ''

            # Castling
            if move[0] in [101, 103]:

                if tense == 'past':
                    sentence += 'castled on the Queen side.'
                elif tense == 'present':
                    sentence += 'castle on the Queen side.'
                elif tense == 'present progressive':
                    sentence += 'castling on the Queen side.'

            elif move[0] in [102, 104]:

                if tense == 'past':
                    sentence += 'castled on the King side.'
                elif tense == 'present':
                    sentence += 'castle on the King side.'
                elif tense == 'present progressive':
                    sentence += 'castling on the King side.'

            else:
                # Piece capture
                if not move[3] == '-':

                    if tense == 'past':
                        sentence += ('captured a {} '.format(write_piece_name(move[3])))
                    elif tense == 'present':
                        sentence += ('capture a {} '.format(write_piece_name(move[3])))
                    elif tense == 'present progressive':
                        sentence += ('capturing a {} '.format(write_piece_name(move[3])))

                    # If there is no Pawn promotion
                    if not (move[1].upper() == 'P' and ((move[2] < 8) or (move[2] > 55))):
                        sentence += ('at {} with a {} from {}.'.format(write_coordinates(move[2]), write_piece_name(move[1]), write_coordinates(move[0])))

                    # If there is also a Pawn promotion
                    else:
                        sentence += 'and '

                # No piece capture and no promotion (plain move)
                elif not (move[1].upper() == 'P' and ((move[2] < 8) or (move[2] > 55))):

                    if tense == 'past':
                        sentence += ('moved a {} from {} to {}.'.format(write_piece_name(move[1]), write_coordinates(move[0]), write_coordinates(move[2])))
                    elif tense == 'present':
                        sentence += ('move a {} from {} to {}.'.format(write_piece_name(move[1]), write_coordinates(move[0]), write_coordinates(move[2])))
                    elif tense == 'present progressive':
                        sentence += ('moving a {} from {} to {}.'.format(write_piece_name(move[1]), write_coordinates(move[0]), write_coordinates(move[2])))

                # Pawn promotion. No elif because it can follow the piece capture
                if move[1].upper() == 'P' and ((move[2] < 8) or (move[2] > 55)):

                    if tense == 'past':
                        sentence += ('promoted a Pawn by moving it from {} to {}.'.format(write_coordinates(move[0]), (write_coordinates(move[2]))))
                    elif tense == 'present':
                        sentence += ('promote a Pawn by moving it from {} to {}.'.format(write_coordinates(move[0]), (write_coordinates(move[2]))))
                    elif tense == 'present progressive':
                        sentence += ('promoting a Pawn by moving it from {} to {}.'.format(write_coordinates(move[0]), (write_coordinates(move[2]))))

            # Make the 1st character upper case
            if not lower_case:
                sentence = sentence[0].upper() + sentence[1:]

            return sentence

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def write_exchange_move(current_player_name, opponent_name, captured_piece_1, move, tense, lower_case):

        # tenses:
        # 'past' - moved
        # 'present' - move
        # 'present progressive' - moving

        # exchange your Rook for Computer's Queen by moving a Rook from D2 to H2.
        # exchange your Rook for Computer's Queen and promote a Pawn by moving it from D2 to H2.

        try:

            if tense == 'past':
                sentence = 'exchanged '
            elif tense == 'present':
                sentence = 'exchange '
            elif tense == 'present progressive':
                sentence = 'exchanging '

            if current_player_name == 'you':
                sentence += 'your '
            elif current_player_name == 'a':
                sentence += 'a '
            else:
                sentence += (current_player_name + "'s ")

            sentence += write_piece_name(captured_piece_1)

            sentence += ' for '

            if opponent_name == 'you':
                sentence += 'your '
            elif opponent_name == 'a':
                sentence += 'a '
            else:
                sentence += (opponent_name + "'s ")

            sentence += write_piece_name(move[3])

            sentence += ' by '

            if True:

                tense = 'present progressive'

                # No piece capture and no promotion (plain move)
                if not (move[1].upper() == 'P' and ((move[2] < 8) or (move[2] > 55))):

                    if tense == 'past':
                        sentence += ('moved a {} from {} to {}.'.format(write_piece_name(move[1]), write_coordinates(move[0]), write_coordinates(move[2])))
                    elif tense == 'present':
                        sentence += ('move a {} from {} to {}.'.format(write_piece_name(move[1]), write_coordinates(move[0]), write_coordinates(move[2])))
                    elif tense == 'present progressive':
                        sentence += ('moving a {} from {} to {}.'.format(write_piece_name(move[1]), write_coordinates(move[0]), write_coordinates(move[2])))

                # Pawn promotion. No elif because it can follow the piece capture
                if move[1].upper() == 'P' and ((move[2] < 8) or (move[2] > 55)):

                    if tense == 'past':
                        sentence += ('promoted a Pawn by moving it from {} to {}.'.format(write_coordinates(move[0]), (write_coordinates(move[2]))))
                    elif tense == 'present':
                        sentence += ('promote a Pawn by moving it from {} to {}.'.format(write_coordinates(move[0]), (write_coordinates(move[2]))))
                    elif tense == 'present progressive':
                        sentence += ('promoting a Pawn by moving it from {} to {}.'.format(write_coordinates(move[0]), (write_coordinates(move[2]))))

            # Make the 1st character upper case
            if not lower_case:
                sentence = sentence[0].upper() + sentence[1:]

            return sentence

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def write_piece_name(code_name):

        try:

            assign_name = {'P': 'Pawn',
                           'N': 'Knight',
                           'B': 'Bishop',
                           'R': 'Rook',
                           'Q': 'Queen',
                           'K': 'King'}

            return assign_name[code_name.upper()]

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def write_coordinates(position):

        try:

            coords = ''
            number_to_letter = 'ABCDEFGH'

            coords += number_to_letter[position % 8]
            coords += str(8 - position // 8)

            return coords

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # Text generation and handling

if True:
    def get_position_from_mouse_click(mouse_coords, board_size, cell_size, upside_down):
        # returns the position of the cell that the mouse clicked on
    
        # Cells are numbered like this:
        #
        #   | 0| 1| 2| 3| 4| 5| 6| 7|
        #   | 8| 9|10|11|12|13|14|15|
        #   |16|17|18|19|20|21|22|23|
        #   |24|25|26|27|28|29|30|31|
        #   |32|33|34|35|36|37|38|39|
        #   |40|41|42|43|44|45|46|47|
        #   |48|49|50|51|52|53|54|55|
        #   |56|57|58|59|60|61|62|63|
        #
        # Additional cells for creating a scenario:
        #
        #   |64|65|66|67|68|
        #   |69|70|71|72|73|
        #
        #         |74|

        try:

            if mouse_coords[0] > int(0.87 * board_size):
                xpos = (mouse_coords[0] - int(1 * board_size)) // cell_size
                ypos = (mouse_coords[1] - int(0.356 * board_size)) // cell_size

                if not upside_down:
                    return (xpos + 8 * ypos)
                else:
                    return 63 - (xpos + 8 * ypos)
            elif mouse_coords[1] < int(0.75 * board_size): # Additional cells for creating a scenario
                xpos = (mouse_coords[0] - int(0.125 * board_size)) // cell_size
                ypos = (mouse_coords[1] - int(0.481 * board_size)) // cell_size
                return (xpos + 5 * ypos) + 64
            else:
                return 74 # <---- Trash can

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def clicked_within_the_board(mouse_coords, board_size):

        try:

            x_coord = mouse_coords[0]
            y_coord = mouse_coords[1]
            if (int(1 * board_size) < x_coord < int(2 * board_size)) and (int(0.356 * board_size) < y_coord < int(1.356 * board_size)):
                return True
            else:
                return False

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def clicked_within_creating_a_scenario_tiles(mouse_coords, board_size):

        try:

            x_coord = mouse_coords[0]
            y_coord = mouse_coords[1]
            if (int(0.125 * board_size) < x_coord < int(0.75 * board_size)) and (int(0.481 * board_size) < y_coord < int(0.731 * board_size)):
                return True
            elif (int(0.375 * board_size) < x_coord < int(0.5 * board_size)) and (int(0.856 * board_size) < y_coord < int(0.981 * board_size)):
                return True
            else:
                return False

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # Mouse click coordinates handling

if True:
    def get_list_of_names():

        try:

            list_of_names = ['Play as a guest', 'New name']

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

        while True:
            try:
                with open(players_text_file_path, 'r') as file:
                    for name in file:
                        list_of_names.append(name[:-1]) # last item is removed from each name because it is a newline character (\n)
                return list_of_names

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def add_new_name(new_name):

        while True:
            try:
                with open(players_text_file_path, 'a') as file:
                    file.writelines(new_name + '\n')
                break

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def delete_name(name_to_delete):

        try:

            list_of_names = get_list_of_names()
            list_of_names.remove('Play as a guest')
            list_of_names.remove('New name')
            list_of_names.remove(name_to_delete)

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

        while True:
            try:
                with open(players_text_file_path, 'w') as file:
                    for name in list_of_names:
                        file.write(name + '\n')
                break
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def get_game_scenarios():
        # Retrieves all game scenarios from the text document and stores them in an array
    
        # line 1: board + castling_info + current_color
        # line 2: white player's name
        # line 3: black player's name
        # line 4: name of the game scenario
        # line 1 of the next game scenario
        # .........................
        # .........................

        while True:
            try:
                with open(game_scenarios_text_file_path, 'r') as file:

                    game_scenarios = []
                    n = 0
                    for line in file:

                        if n % 4 == 0 and not line == '\n': # line 1
                            board = []
                            castling_info = []
                            for index in range(0, 64):
                                board.append(line[index])
                            for index in range(64, 70):
                                castling_info.append(bool(int(line[index])))
                            current_color = bool(int(line[70]))

                            player = {True: None,
                                      False: None}
                        elif n % 4 == 1: # line 2
                            player[True] = line[:-1] # remove the newline character (\n)
                        elif n % 4 == 2: # line 3
                            player[False] = line[:-1] # remove the newline character (\n)
                        else: # line 4
                            scenario_name = line[:-1] # remove the newline character (\n)
                            game_scenarios.append([scenario_name, board, castling_info, current_color, player])

                        n += 1 
                return game_scenarios

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def get_a_game_scenario(scenario_name):

        try:

            game_scenarios = get_game_scenarios()

            for game_scenario in game_scenarios:
                if game_scenario[0] == scenario_name:
                    board = game_scenario[1]
                    castling_info = game_scenario[2]
                    current_color = game_scenario[3]
                    player = game_scenario[4]

                    return board, castling_info, current_color, player

            print('Error in get_a_game_scenario, no scenario found with a specified name')

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def add_a_game_scenario(scenario_name, board, castling_info, current_color, player):

        # line 1: board + castling_info + current_color
        # line 2: white player's name
        # line 3: black player's name
        # line 4: name of the game scenario
        # line 1 of the next game scenario
        # .........................
        # .........................

        while True:
            try:
                with open(game_scenarios_text_file_path, 'a') as file:

                    for item in board:
                        file.writelines(item)
                    for item in castling_info:
                        if item == True:
                            file.writelines('1')
                        else:
                            file.writelines('0')
                    if current_color == True:
                        file.writelines('1\n')
                    else:
                        file.writelines('0\n')

                    file.writelines(player[True] + '\n')
                    file.writelines(player[False] + '\n')
                    file.writelines(scenario_name + '\n')
                break
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def delete_a_game_scenario(index_to_delete):
        
        try:

            game_scenarios = get_game_scenarios()
            game_scenarios = game_scenarios[:index_to_delete] + game_scenarios[(index_to_delete + 1):] # Delete

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

        while True:
            try:
                with open(game_scenarios_text_file_path, 'w') as file:
                    for scenario in game_scenarios:
                        scenario_name = scenario[0]
                        board = scenario[1]
                        castling_info = scenario[2]
                        current_color = scenario[3]
                        player = scenario[4]

                        for item in board:
                            file.write(item)
                        for item in castling_info:
                            if item == True:
                                file.write('1')
                            else:
                                file.write('0')
                        if current_color == True:
                            file.write('1\n')
                        else:
                            file.write('0\n')

                        file.write(player[True] + '\n')
                        file.write(player[False] + '\n')
                        file.write(scenario_name + '\n')
                break
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def get_game_history():

        while True:
            try:
                with open(game_history_text_file_path, 'r') as file:

                    game_history = []
                    n = 0
                    for line in file:

                        if n % 4 == 0 and not line == '\n': # line 1

                            winner_name = line[:-1] # remove the newline character (\n)

                        elif n % 4 == 1: # line 2
                            
                            loser_name = line[:-1] # remove the newline character (\n)

                        elif n % 4 == 2: # line 3

                            game_outcome = line[:-1] # remove the newline character (\n)

                        else: # line 4

                            date_of_game = line[:-1] # remove the newline character (\n)
                            game_history.append([winner_name, loser_name, game_outcome, date_of_game])

                        n += 1 
                return game_history

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def get_structured_game_history():
        
        try:

            structured_move_history = []

            registered_names = get_list_of_names()

            game_history = get_game_history()

            names_checked = ['Computer']

            for item in game_history:

                for name in item[:-2]:

                    if (not name in names_checked) and (name in registered_names):

                        percentage_of_wins_overall, percantage_of_wins_against_computer, percentage_of_wins_against_humans = get_percentages_of_wins(name, game_history)

                        average_time_per_move = get_an_average_time_per_move(name)

                        structured_move_history.append([name, average_time_per_move, percantage_of_wins_against_computer, percentage_of_wins_against_humans, percentage_of_wins_overall, 'click here to see'])

                        names_checked.append(name)

            return structured_move_history

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def get_percentages_of_wins(player_name, game_history):

        try:

            games_played_total = 0
            games_played_against_computer = 0
            games_player_against_humans = 0
            
            games_won_total = 0
            games_won_against_computer = 0
            games_won_against_humans = 0

            for winner_name, loser_name, game_outcome, _ in game_history:

                if player_name in [winner_name, loser_name]:
                    games_played_total += 1

                    if 'Computer' in [winner_name, loser_name]:
                        games_played_against_computer += 1
                    else:
                        games_player_against_humans += 1

                if not game_outcome in ['2', '3']: # not stalemate or draw
                    
                    if player_name == winner_name:
                        games_won_total += 1

                        if loser_name == 'Computer':
                            games_won_against_computer += 1
                        else:
                            games_won_against_humans += 1

            if games_played_total == 0:
                percentage_of_wins_overall = 'N/A'
            else:
                percentage_of_wins_overall = str(int(round(((games_won_total / games_played_total) * 100), 0))) + '%'

            if games_played_against_computer == 0:
                percantage_of_wins_against_computer = 'N/A'
            else:
                percantage_of_wins_against_computer = str(int(round(((games_won_against_computer / games_played_against_computer) * 100), 0))) + '%'

            if games_player_against_humans == 0:
                percentage_of_wins_against_humans = 'N/A'
            else:
                percentage_of_wins_against_humans = str(int(round(((games_won_against_humans / games_player_against_humans) * 100), 0))) + '%'

            return percentage_of_wins_overall, percantage_of_wins_against_computer, percentage_of_wins_against_humans

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def get_list_of_games(player_name):

        try:

            game_history = get_game_history()
            max_number_of_lines_per_page = 16
            sentences = []

            for winner_name, loser_name, game_outcome, date_of_game in game_history:

                game_outcome = int(game_outcome)

                if player_name in [winner_name, loser_name]:
                    
                    if not player_name == winner_name:
                        text = player_name + ' played a game with ' + winner_name
                    else:
                        text = player_name + ' played a game with ' + loser_name

                    text += (' on ' + date_of_game + '. ')

                    if game_outcome in [-1, 1]:
                        text += (winner_name + ' won by checkmating ' + loser_name + '.')
                    elif game_outcome == 2:
                        text += ('Game ended after a stalemate.')
                    elif game_outcome == 3:
                        text += ('Game resulted in a draw.')
                    elif game_outcome == 4:
                        text += (winner_name + ' won because ' + loser_name + ' forfeited.')
                    elif game_outcome == 5:
                        text += (winner_name + ' won because ' + loser_name + ' ran out of time.')

                    sentences.append(text)

            lines_on_page = 0
            page = []
            pages = []
            for line_no, sentence in enumerate(sentences):
                page.append(sentence)
                lines_on_page += 1
                if lines_on_page == max_number_of_lines_per_page or line_no == (len(sentences) - 1):
                    pages.append(page[:])
                    lines_on_page = 0
                    page = []

            return pages

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def add_game_result_to_game_history(winner_name, loser_name, game_outcome):
        
        while True:
            try:
                with open(game_history_text_file_path, 'a') as file:

                    file.writelines(winner_name + '\n')
                    file.writelines(loser_name + '\n')
                    file.writelines(str(game_outcome) + '\n')

                    x = datetime.datetime.now()

                    digit_to_month = [None, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

                    text = str(x.day)

                    if x.day in [1, 21, 31]:
                        text += 'st of '
                    elif x.day in [2, 22, 32]:
                        text += 'nd of '
                    elif x.day in [3, 23, 33]:
                        text += 'rd of '
                    else:
                        text += 'th of '

                    text += (digit_to_month[x.month] + ' ' + str(x.year))

                    file.writelines(text + '\n')

                break
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def get_average_times_per_move():

        while True:
            try:
                with open(average_times_per_move_text_file_path, 'r') as file:

                    average_times_per_move = []
                    n = 0
                    for line in file:

                        if n % 2 == 0 and not line == '\n': # line 1

                            name = line[:-1] # remove the newline character (\n)

                        else: # line 2
                            
                            av_time = float(line[:-1]) # remove the newline character (\n)

                            average_times_per_move.append([name, av_time])

                        n += 1 
                return average_times_per_move

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def get_an_average_time_per_move(player_name):

        try:

            average_times_per_move= get_average_times_per_move()

            for name, av_time in average_times_per_move:
                if name == player_name:

                    if not av_time // 60 == 0:
                        text = ('{} min  {} sec'.format(int(av_time // 60), round(av_time % 60), 1)) # Display as minutes + seconds
                    else:
                        text = ('{} seconds'.format(av_time)) # Display as seconds only

                    return text

            return 'N/A'

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def alter_average_times_per_move(player, average_time_per_move_white, average_time_per_move_black):
        
        try:
            average_times_per_move = get_average_times_per_move()

            for current_color in [True, False]:

                if (current_color == True and not average_time_per_move_white == None) or (current_color == False and not average_time_per_move_black == None):
                    
                    current_name = player[current_color]

                    name_found = False
                    for index, item in enumerate(average_times_per_move):

                        if item[0] == current_name:
                            if current_color == True: # White player
                                average_times_per_move[index][1] = round((0.5 * (item[1] + average_time_per_move_white)), 1) # average
                            else: # Black player
                                average_times_per_move[index][1] = round((0.5 * (item[1] + average_time_per_move_black)), 1) # average
                            name_found = True
                            break

                    if not name_found:
                        if current_color == True: # White player
                            average_times_per_move.append([current_name, average_time_per_move_white])
                        else: # Black player
                            average_times_per_move.append([current_name, average_time_per_move_black])

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

        while True:
            try:
                with open(average_times_per_move_text_file_path, 'w') as file:
                    for name, av_time in average_times_per_move:

                        file.write(name + '\n')
                        file.write(str(av_time) + '\n')

                break
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def get_board_size():

        while True:
            try:
                with open(window_size_text_file_path, 'r') as file:

                    for n, line in enumerate(file):

                        if n == 0:

                            board_size = int(line)
                            return board_size
                
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def alter_board_size(board_size, difference):

        while True:
            try:
                with open(window_size_text_file_path, 'w') as file:

                    file.write(str(int(board_size + difference)))
                    return

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    def add_exception_to_log(function_name, reason, exit = True, delay = 0):
        
        while True:
            try:
                print()
                print('Error')
                print('Function: ' + function_name)
                print('Reason: ' + str(reason))
                print()
                
                with open(event_log_file_path, 'a') as file:

                    file.writelines(str(datetime.datetime.now()) + '\n')
                    file.writelines('Function: ' + function_name + '\n')
                    file.writelines('Reason: ' + str(reason) + '\n\n')

                if exit == True:
                    print('Program will restart shortly')
                    print()
                    time.sleep(delay)
                    os.execv(sys.executable, ['python'] + sys.argv)
                break
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e, exit = False)

    pass # Text file handling

if True:
    def print_board(board):
        # Prints the board in console
        # For testing only

        try:
            print()
            for a in range(8):
                for b in range(8):
                    print(board[a*8 + b], end = ' ')
                print()
            print()

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # Subroutines for testing (not essential for running the program)

def automatically_select_a_name(already_selected_name):

    try:

        list_of_names = get_list_of_names()

        for name in list_of_names:
            if not name in ['Play as a guest', 'New name'] and not name == already_selected_name:
                return name

    except Exception as e:
        function_name = inspect.currentframe().f_code.co_name
        add_exception_to_log(function_name, e)

def validate_selected_cell(board, current_position, current_color, state):
    # Only allows humans to select pieces with their own color

    # Current_color:
    # True = white
    # False = black

    try:

        if state == 'waiting for 1st click':
            if current_color == True and board[current_position].islower():
                return current_position, 'waiting for 2nd click'
            elif current_color == False and board[current_position].isupper():
                return current_position, 'waiting for 2nd click'
            else:
                return None, 'waiting for 1st click'

        else: # Creating a scenario, allow selection of pieces regardless of color
            if current_position > 63:
                if current_position == 74:
                    return None, 'creating a scenario, waiting for 1st click'
                else:
                    return current_position, 'creating a scenario, waiting for 2nd click'
            if not board[current_position] == '-':
                return current_position, 'creating a scenario, waiting for 2nd click'
            else:
                return None, 'creating a scenario, waiting for 1st click'

    except Exception as e:
        function_name = inspect.currentframe().f_code.co_name
        add_exception_to_log(function_name, e)

def calculate_average_time_per_move(move_times):

    try:

        sum = 0

        for move_time in move_times:
            sum += move_time

        # round an average to 1 d. p.
        return round(sum / len(move_times), 1)

    except Exception as e:
        function_name = inspect.currentframe().f_code.co_name
        add_exception_to_log(function_name, e)

def approximate_castling_info(board):

    try:

        castling_info = [True, True, True, True, True, True]

        if board[0] == 'R':
            castling_info[0] = False
        if board[4] == 'K':
            castling_info[1] = False
        if board[7] == 'R':
            castling_info[2] = False
        if board[56] == 'r':
            castling_info[3] = False
        if board[60] == 'k':
            castling_info[4] = False
        if board[63] == 'r':
            castling_info[5] = False

        return castling_info

    except Exception as e:
        function_name = inspect.currentframe().f_code.co_name
        add_exception_to_log(function_name, e)

if True:
    def make_move(board, current_position, new_position, castling_info, move_history, simulation):

        try:

            if not simulation:
                if not move_history == []:
                    captured_pieces = move_history[-1][-2][:]
                else:
                    captured_pieces = []

            if new_position in [101, 102, 103, 104]: # Castling
                castle(new_position, board, castling_info, move_history, simulation)
            else:

                if not simulation:
                    if not board[new_position] == '-':
                        captured_pieces.append(board[new_position])
                    move_history.append([current_position, board[current_position], new_position, board[new_position]])

                if board[current_position] == 'p' and new_position < 8: # White pawn promotion
                    board[new_position] = 'q'
                elif board[current_position] == 'P' and new_position > 55: # Black pawn promotion
                    board[new_position] = 'Q'

                else:
                    alter_castling_info(castling_info, current_position, new_position) # Making an ordinary move
                    board[new_position] = board[current_position]

                board[current_position] = '-'

            # This function is called with simulation == True when moves are simulated through minimax
            # The following line saves the castling info so that when 'undo a move' is used, this info can be recovered
            # This information recovery is unnecesary for minimax and disabled for efficience reasons
            if not simulation:
                move_history[-1].append(captured_pieces[:])
                move_history[-1].append(castling_info[:])

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def undo_a_move(board, move_history):

        try:

            if move_history[-1][0] in [101, 102, 103, 104]: # Castling
                undo_castle(board, move_history)
            else:
                board[move_history[-1][0]] = move_history[-1][1]
                board[move_history[-1][2]] = move_history[-1][3]

            del move_history [-1]

            return

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def make_move_when_creating_a_scenario(board, current_position, new_position):

        try:

            small_board = ['q', 'r', 'b', 'n', 'p', 'Q', 'R', 'B', 'N', 'P']

            if current_position > 63:
                deleted_piece = None
                board[new_position] = small_board[current_position - 64]
            elif new_position == 74: # Delete piece
                deleted_piece = board[current_position]
                board[current_position] = '-'
            else:
                deleted_piece = None
                board[new_position] = board[current_position]
                board[current_position] = '-'

            return deleted_piece

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def castle(position, board, castling_info, move_history, simulation):

        try:

            if position == 101: # Black queenside (left) castling
                board[2] = 'K'
                board[3] = 'R'
                board[4] = '-'
                board[0] = '-'
                castling_info[1] = True
                castling_info[0] = True
                if not simulation:
                    move_history.append([101])
            elif position == 102: # Black kingside (right) castling
                board[6] = 'K'
                board[5] = 'R'
                board[4] = '-'
                board[7] = '-'
                castling_info[1] = True
                castling_info[2] = True
                if not simulation:
                    move_history.append([102])
            elif position == 103: # White queenside (left) castling
                board[58] = 'k'
                board[59] = 'r'
                board[60] = '-'
                board[56] = '-'
                castling_info[4] = True
                castling_info[3] = True
                if not simulation:
                    move_history.append([103])
            else: # position == 104 # White kingside (right) castling
                board[62] = 'k'
                board[61] = 'r'
                board[60] = '-'
                board[63] = '-'
                castling_info[4] = True
                castling_info[5] = True
                if not simulation:
                    move_history.append([104])

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def undo_castle(board, move_history):

        try:

            if move_history[-1][0] == 101: # Black queenside (left) castling
                board[2] = '-'
                board[3] = '-'
                board[4] = 'K'
                board[0] = 'R'
            elif move_history[-1][0] == 102: # Black kingside (right) castling
                board[6] = '-'
                board[5] = '-'
                board[4] = 'K'
                board[7] = 'R'
            elif move_history[-1][0] == 103: # White queenside (left) castling
                board[58] = '-'
                board[59] = '-'
                board[60] = 'k'
                board[56] = 'r'
            else: # move_history[-1][0] == 104 # White kingside (right) castling
                board[62] = '-'
                board[61] = '-'
                board[60] = 'k'
                board[63] = 'r'

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def alter_castling_info(castling_info, current_position, new_position):

        try:

            if current_position == 0 or new_position == 0:
                castling_info[0] = True
            elif current_position == 4:
                castling_info[1] = True
            elif current_position == 7 or new_position == 7:
                castling_info[2] = True
            elif current_position == 56 or new_position == 56:
                castling_info[3] = True
            elif current_position == 60:
                castling_info[4] = True
            elif current_position == 63 or new_position == 63:
                castling_info[5] = True

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def sort_captured_pieces(captured_pieces):

        try:

            # Adds a new captured piece to the list in the following order:
            piece_to_digit = {'q': 0,
                              'r': 1,
                              'b': 2,
                              'n': 3,
                              'p': 4,
                              'Q': 5,
                              'R': 6,
                              'B': 7,
                              'N': 8,
                              'P': 9}

            digit_to_piece = 'qrbnpQRBNP'

            digitalised_captured_pieces = []

            for piece in captured_pieces:
                digitalised_captured_pieces.append(piece_to_digit[piece])

            captured_pieces = []
            digitalised_captured_pieces.sort()

            for digit in digitalised_captured_pieces:
                captured_pieces.append(digit_to_piece[digit])

            return captured_pieces

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def create_attack_list(board, current_position, current_color, castling_info, board_after_best_move):

        try:

            # Adds pieces to the list in the following order:
            piece_to_digit = {'Q': 0,
                              'R': 1,
                              'B': 2,
                              'N': 3,
                              'P': 4}

            digit_to_piece = 'QRBNP'

            legal_move_list = create_general_legal_move_list(board, current_position, current_color, castling_info)
            attack_list = []

            for coord in legal_move_list:
                if not board[coord] in ['-', 'k', 'K', 'p', 'P']:
                    if (not board_after_best_move == None and board[coord] == board_after_best_move[coord]) or board_after_best_move == None:
                        attack_list.append(board[coord].upper())

            digitalised_attack_list = []

            for piece in attack_list:
                digitalised_attack_list.append(piece_to_digit[piece])

            attack_list = []
            digitalised_attack_list.sort()

            for digit in digitalised_attack_list:
                attack_list.append(digit_to_piece[digit])

            return attack_list

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def piece_is_more_significant(piece_1, piece_2):
        # Returns True if piece_1 has a higher significance than a piece_2

        try:

            piece_to_digit = {'Q': 0,
                              'R': 1,
                              'B': 2,
                              'N': 3,
                              'P': 4}

            if piece_to_digit[piece_1.upper()] < piece_to_digit[piece_2.upper()]:
                return True
            else:
                return False

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    if True:
        def create_general_legal_move_list(board, current_position, current_color, castling_info):

            try:

                legal_move_list = []

                if board[current_position].upper() == 'K': # king
                    legal_move_list = king_create_legal_move_list(board, current_position, current_color, legal_move_list, castling_info)
                else:
                    king_position = find_king_position(board, current_color)

                    if board[current_position].upper() == 'R': # rook
                        legal_move_list = rook_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position)
                    elif board[current_position].upper() == 'B': # bishop
                        legal_move_list = bishop_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position)
                    elif board[current_position].upper() == 'N': # knight
                        legal_move_list = knight_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position)
                    elif board[current_position] == 'p': # white pawn
                        legal_move_list = white_pawn_create_legal_move_list(board, current_position, legal_move_list, king_position)
                    elif board[current_position] == 'P': # black pawn
                        legal_move_list = black_pawn_create_legal_move_list(board, current_position, legal_move_list, king_position)
                    else: # queen
                        # Queen moves like both a rook and a bishop
                        # Therefore, its list is composed of both rook's and bishop's lists combined together
                        legal_move_list = rook_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position)
                        legal_move_list = bishop_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position)

                return legal_move_list

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        # ROOK
        def rook_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position):
    
            try:

                # lower case is white, upper case is black
                # Current_color:
                # True = white
                # False = black
                for difference in (-1, 1, -8, 8):
                    new_position = current_position
                    while True:
                        new_position += difference
                        if new_position < 0 or new_position > 63 or (difference == -1 and (current_position % 8 == 0)) or (difference == 1 and (current_position % 8 == 7)) or (current_color == True and board[new_position].islower()) or (current_color == False and board[new_position].isupper()):
                            break
                        elif (current_color == True and board[new_position].isupper()) or (current_color == False and board[new_position].islower()) or (difference == -1 and (new_position % 8 == 0)) or (difference == 1 and (new_position % 8 == 7)):
                            if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                                legal_move_list.append(new_position)
                            break
                        else:
                            if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                                legal_move_list.append(new_position)
                return legal_move_list

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        # BISHOP
        def bishop_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position):
    
            try:

                # lower case is white, upper case is black
                # Current_color:
                # True = white
                # False = black
                for difference in (-7, 7, -9, 9):
                    new_position = current_position
                    while True:
                        new_position += difference
                        if new_position < 0 or new_position > 63 or ((difference in [-9, 7]) and (current_position % 8 == 0)) or ((difference in [-7, 9]) and (current_position % 8 == 7)) or (current_color == True and board[new_position].islower()) or (current_color == False and board[new_position].isupper()):
                            break
                        elif (current_color == True and board[new_position].isupper()) or (current_color == False and board[new_position].islower()) or ((difference in [-9, 7]) and (new_position % 8 == 0)) or ((difference in [-7, 9]) and (new_position % 8 == 7)):
                            if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                                legal_move_list.append(new_position)
                            break
                        else:
                            if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                                legal_move_list.append(new_position)
                return legal_move_list

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        # KNIGHT
        def knight_create_legal_move_list(board, current_position, current_color, legal_move_list, king_position):
    
            try:

                # lower case is white, upper case is black
                # Current_color:
                # True = white
                # False = black
                for difference in (-6, 6, -10, 10, -15, 15, -17, 17):
                    new_position = current_position + difference
                    if not (new_position < 0 or
                            new_position > 63 or
                            ((difference == -10 or difference == 6) and current_position % 8 < 2) or
                            ((difference == -17 or difference == 15) and current_position % 8 == 0) or
                            ((difference == -6 or difference == 10) and current_position % 8 > 5) or
                            ((difference == -15 or difference == 17) and current_position % 8 == 7) or
                            (current_color == True and board[new_position].islower()) or
                            (current_color == False and board[new_position].isupper())):
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                return legal_move_list

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        # WHITE PAWN
        def white_pawn_create_legal_move_list(board, current_position, legal_move_list, king_position):
    
            try:

                # lower case is white, upper case is black
                current_color = True # True = white

                for difference in (-7, -8, -9, -16):
                    new_position = current_position + difference
                    if difference == -16 and current_position > 47 and board[current_position - 8] == '-' and board[new_position] == '-':
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                    elif difference == -8 and new_position > -1 and board[new_position] == '-':
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                    elif difference == -9 and new_position > -1 and not (current_position % 8 == 0) and board[new_position].isupper():
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                    elif difference == -7 and new_position > -1 and not (current_position % 8 == 7) and board[new_position].isupper():
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                return legal_move_list

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        # BLACK PAWN
        def black_pawn_create_legal_move_list(board, current_position, legal_move_list, king_position):

            try:

                # lower case is white, upper case is black
                current_color = False # False = black

                for difference in (7, 8, 9, 16):
                    new_position = current_position + difference
                    if difference == 16 and current_position < 16 and board[current_position + 8] == '-' and board[new_position] == '-':
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                    elif difference == 8 and new_position < 64 and board[new_position] == '-':
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                    elif difference == 7 and new_position < 64 and not (current_position % 8 == 0) and board[new_position].islower():
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                    elif difference == 9 and new_position < 64 and not (current_position % 8 == 7) and board[new_position].islower():
                        if not piece_under_attack(board[:], current_position, new_position, king_position, current_color, True):
                            legal_move_list.append(new_position)
                return legal_move_list

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        # KING
        def king_create_legal_move_list(board, current_position, current_color, legal_move_list, castling_info):

            try:

                # lower case is white, upper case is black
                # Current_color:
                # True = white
                # False = black
                for difference in (-1, 1, -7, 7, -8, 8, -9, 9):
                    new_position = current_position + difference
                    if not (new_position < 0 or
                            new_position > 63 or
                            ((difference in [-9, -1, 7]) and current_position % 8 == 0) or
                            ((difference in [-7, 1, 9]) and current_position % 8 == 7) or
                            (current_color == True and board[new_position].islower()) or
                            (current_color == False and board[new_position].isupper())):

                        if not piece_under_attack(board[:], current_position, new_position, new_position, current_color, True):
                            legal_move_list.append(new_position)

                # castling_info = [(black left rook moved?), (black king moved?), ((black right rook moved?),
                #                  (white left rook moved?), (white king moved?), ((white right rook moved?)]
                # index: [0, 1, 2,
                #         3, 4, 5]

                # castling positions:
                # 101 - Black, queenside (left)
                # 102 - Black, kingside (right)
                # 103 - White, queenside (left)
                # 104 - White, kingside (right)

                # castling
                if castling_info[4] == False and current_color == True and not piece_under_attack(board, 0, 0, current_position, current_color, False):
                    if castling_info[3] == False and board[57] == '-' and board[58] == '-' and board[59] == '-':
                        new_position = 58
                        if not piece_under_attack(board[:], current_position, new_position, new_position, current_color, True):
                            legal_move_list.append(103)
                    if castling_info[5] == False and board[61] == '-' and board[62] == '-':
                        new_position = 62
                        if not piece_under_attack(board[:], current_position, new_position, new_position, current_color, True):
                            legal_move_list.append(104)
                if castling_info[1] == False and current_color == False and not piece_under_attack(board, 0, 0, current_position, current_color, False):
                    if castling_info[0] == False and board[1] == '-' and board[2] == '-' and board[3] == '-':
                        new_position = 2
                        if not piece_under_attack(board[:], current_position, new_position, new_position, current_color, True):
                            legal_move_list.append(101)
                    if castling_info[2] == False and board[5] == '-' and board[6] == '-':
                        new_position = 6
                        if not piece_under_attack(board[:], current_position, new_position, new_position, current_color, True):
                            legal_move_list.append(102)

                return legal_move_list

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        def find_king_position(board, current_color):

            try:

                # Current_color:
                # True = white
                # False = black
                if current_color == True:
                    for position in range(64):
                        if board[position] == 'k':
                            return position
                else: # current_color == False
                    for position in range(64):
                        if board[position] == 'K':
                            return position

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        def piece_under_attack(board, old_position, current_position, piece_position, current_color, board_needs_modifying):

            try:

                # If board_needs_modifying is True, makes a move and checks if a piece is under attack after it
                # Looks for attacks from every kind of piece
    
                # Current_color:
                # True = white
                # False = black

                if board_needs_modifying:
                    board[current_position] = board[old_position]
                    board[old_position] = '-'

                current_position = piece_position

                # looks for BISHOPS, QUEENS, PAWNS and a KING on diagonals (KING and PAWNS is only on the 1st iteration, PAWNS are specific to the color)
                for difference in (-7, 7, -9, 9):
                    new_position = current_position
                    first_iteration = True
                    while True:
                        new_position += difference
                        if new_position < 0 or new_position > 63 or ((difference == -9 or difference == 7) and (current_position % 8 == 0)) or ((difference == 9 or difference == -7) and (current_position % 8 == 7)) or (current_color == True and not (board[new_position] in ['-', 'B', 'Q'] or (first_iteration == True and (board[new_position] == 'K' or (difference in [-7, -9] and board[new_position] == 'P'))))) or (current_color == False and not (board[new_position] in ['-', 'b', 'q'] or (first_iteration == True and (board[new_position] == 'k' or (difference in [7, 9] and board[new_position] == 'p'))))):
                            break
                        elif (current_color == True and (board[new_position] in ['B', 'Q'] or (first_iteration == True and (board[new_position] == 'K' or (difference in [-7, -9] and board[new_position] == 'P'))))) or (current_color == False and (board[new_position] in ['b', 'q'] or (first_iteration == True and (board[new_position] == 'k' or (difference in [7, 9] and board[new_position] == 'p'))))):
                            return True
                        elif ((difference == -9 or difference == 7) and (new_position % 8 == 0)) or ((difference == 9 or difference == -7) and (new_position % 8 == 7)):
                            break
                        first_iteration = False

                # Looks for ROOKS, QUEENS and a KING on verticals and horisontals (KING is only on the 1st iteration)
                for difference in (-1, 1, -8, 8):
                    new_position = current_position
                    first_iteration = True
                    while True:
                        new_position += difference
                        if new_position < 0 or new_position > 63 or (difference == -1 and (current_position % 8 == 0)) or (difference == 1 and (current_position % 8 == 7)) or (current_color == True and not (board[new_position] in ['-', 'R', 'Q'] or (first_iteration == True and board[new_position] == 'K'))) or (current_color == False and not (board[new_position] in ['-', 'r', 'q'] or (first_iteration == True and board[new_position] == 'k'))):
                            break
                        elif (current_color == True and (board[new_position] in ['R', 'Q'] or (first_iteration == True and board[new_position] == 'K'))) or (current_color == False and (board[new_position] in ['r', 'q'] or (first_iteration == True and board[new_position] == 'k'))):
                            return True
                        elif (difference == -1 and (new_position % 8 == 0)) or (difference == 1 and (new_position % 8 == 7)):
                            break
                        first_iteration = False

                # Looks for Knights
                for difference in (-6, 6, -10, 10, -15, 15, -17, 17):
                    new_position = current_position + difference
                    if (not (new_position < 0 or
                            new_position > 63 or
                            ((difference == -10 or difference == 6) and current_position % 8 < 2) or
                            ((difference == -17 or difference == 15) and current_position % 8 == 0) or
                            ((difference == -6 or difference == 10) and current_position % 8 > 5) or
                            ((difference == -15 or difference == 17) and current_position % 8 == 7))) and ((current_color == True and board[new_position] == 'N') or (current_color == False and board[new_position] == 'n')):
                        return True

                return False 
        
            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        def create_legal_move_list_for_ALL_pieces(board, current_color, castling_info):
            # Creates a list for all possible legal current positions
            
            # [[current_position, new_position], [current_position, new_position], [current_position, new_position], ............]

            try:

                legal_move_list_for_ALL_pieces = []

                # Looks through every possible legal move
                for current_position in range(64):

                    if (board[current_position].islower() and current_color == True) or (board[current_position].isupper() and current_color == False):
                        legal_move_list = create_general_legal_move_list(board, current_position, current_color, castling_info)

                        for new_position in legal_move_list:
                            legal_move_list_for_ALL_pieces.append([current_position, new_position])

                return legal_move_list_for_ALL_pieces

            except Exception as e:
                function_name = inspect.currentframe().f_code.co_name
                add_exception_to_log(function_name, e)

        if True:
            def generate_legal_move_list_for_creating_a_scenario(board, current_position):

                try:

                    legal_move_list = []

                    # Board
                    for new_position in range(64):
                        if not illegal_move_when_creating_a_game_scenario(board, current_position, new_position):
                            legal_move_list.append(new_position)

                    # Trash can
                    if not illegal_move_when_creating_a_game_scenario(board, current_position, 74):
                        legal_move_list.append(74)

                    return legal_move_list

                except Exception as e:
                    function_name = inspect.currentframe().f_code.co_name
                    add_exception_to_log(function_name, e)

            def illegal_move_when_creating_a_game_scenario(board, current_position, new_position):

                try:

                    small_board = ['q', 'r', 'b', 'n', 'p', 'Q', 'R', 'B', 'N', 'P']

                    if new_position == 74: # Trash can
                        if current_position > 63:
                            return True
                        elif board[current_position].upper() == 'K':
                            return True
                        elif causes_check(board[:], current_position, new_position):
                            return True
                        else:
                            return False

                    if current_position > 63:
                        if maximum_number_of_specific_pieces_reached(board, small_board[current_position - 64]):
                            return True

                    if not board[new_position] == '-':
                        return True
                    elif causes_check(board[:], current_position, new_position):
                        return True
                    elif (current_position > 63 and small_board[current_position - 64] == 'B') or (current_position < 64 and board[current_position] == 'B'): # If selected piece is a BLACK bishop
                        positions = get_all_positions_of_specific_piece(board, 'B')

                        for position in positions:
                            if not position == current_position:
                                if get_cell_color(board, position) == get_cell_color(board, new_position): # Cannot place bishops on cells with the same color
                                    return True

                    elif (current_position > 63 and small_board[current_position - 64] == 'b') or (current_position < 64 and board[current_position] == 'b'): # If selected piece is a WHITE bishop
                        positions = get_all_positions_of_specific_piece(board, 'b')

                        for position in positions:
                            if not position == current_position:
                                if get_cell_color(board, position) == get_cell_color(board, new_position): # Cannot place bishops on cells with the same color
                                    return True

                    elif (current_position > 63 and small_board[current_position - 64] == 'P') or (current_position < 64 and board[current_position] == 'P'): # If selected piece is a BLACK pawn
                        if new_position < 8 or new_position > 55: # Cannot place Pawns at the horizontal edge
                            return True

                    elif (current_position > 63 and small_board[current_position - 64] == 'p') or (current_position < 64 and board[current_position] == 'p'): # If selected piece is a BLACK pawn
                        if new_position < 8 or new_position > 55: # Cannot place Pawns at the horizontal edge
                            return True

                    else:
                        return False

                except Exception as e:
                    function_name = inspect.currentframe().f_code.co_name
                    add_exception_to_log(function_name, e)

            def causes_check(board, current_position, new_position):
            
                try:

                    make_move_when_creating_a_scenario(board, current_position, new_position)

                    current_color = False

                    king_position = find_king_position(board, current_color)
                    if piece_under_attack(board, None, None, king_position, current_color, False):
                        return True

                    return False

                except Exception as e:
                    function_name = inspect.currentframe().f_code.co_name
                    add_exception_to_log(function_name, e)

            def maximum_number_of_specific_pieces_reached(board, specific_piece):
            
                try:

                    if specific_piece.upper() in ['R', 'B', 'N']:
                        if count_number_of_specific_pieces(board, specific_piece) == 2:
                            return True
                    elif specific_piece.upper() == 'P' and count_number_of_specific_pieces(board, specific_piece) == 8:
                            return True
                    else: # Piece is either a Pawn or a Queen. Maximum total of Pawns and Queens is 9, but maximum number of Pawns is 8
                        if specific_piece.islower():
                            if count_number_of_specific_pieces(board, 'p') + count_number_of_specific_pieces(board, 'q') == 9:
                                return True
                        else: # specific_piece.isupper():
                            if count_number_of_specific_pieces(board, 'P') + count_number_of_specific_pieces(board, 'Q') == 9:
                                return True
                    return False

                except Exception as e:
                    function_name = inspect.currentframe().f_code.co_name
                    add_exception_to_log(function_name, e)

            def count_number_of_specific_pieces(board, specific_piece):

                try:

                    n = 0
                    for piece in board:
                        if piece == specific_piece:
                            n += 1
                    return n

                except Exception as e:
                    function_name = inspect.currentframe().f_code.co_name
                    add_exception_to_log(function_name, e)

            def get_cell_color(board, desired_position):

                try:

                    counter = 1 # this counter is needed to allocate the color to the cells.
                    # counter does not count all cells directly - when moving from one line to another it is incremented twice
                    position = 0 # position of a certain cell in a 1D array

                    for a in range(8):
                        for b in range(8):

                            if position == desired_position:
                                if counter % 2 == 0:
                                    return 'black'
                                else:
                                    return 'white'

                            counter += 1
                            position += 1

                        counter += 1

                except Exception as e:
                    function_name = inspect.currentframe().f_code.co_name
                    add_exception_to_log(function_name, e)

            def get_all_positions_of_specific_piece(board, specific_piece):

                try:

                    positions = []
                    for n in range(64):
                        if board[n] == specific_piece:
                            positions.append(n)
                    return positions

                except Exception as e:
                    function_name = inspect.currentframe().f_code.co_name
                    add_exception_to_log(function_name, e)

            pass # Legal list for creating new scenarios

        pass # Create legal move list

    pass # Game mechanics

if True:
    def create_feedback(feedback_type, board, current_color, castling_info, move_history, player, initial_castling_info):
        
        try:

            start_time = time.time()

            # Feedback types:
            # 0. Why did {name} make this move?
            # 1. What move should I make?
            # 2. Was that a strong move?
            # 3. What other move could I make?

            if feedback_type == 0:
                feedback_sentences = why_did_opponent_make_this_move(board, current_color, castling_info, move_history, player, initial_castling_info)
            elif feedback_type == 1:
                feedback_sentences = what_move_should_i_make(board, current_color, castling_info, move_history, player)
            elif feedback_type == 2:
                feedback_sentences = was_that_a_strong_move(board, current_color, castling_info, move_history, player, initial_castling_info)
            elif feedback_type == 3:
                feedback_sentences = what_other_move_could_i_make(board, current_color, castling_info, move_history, player, initial_castling_info)

            feedback_lines = []

            for sentence in feedback_sentences:
                text_lines = split_text_into_lines(sentence, 0.5275)
                for line in text_lines:
                    feedback_lines.append(line)

            end_time = time.time()
            print('Feedback generation time: {}s'.format(round(end_time - start_time, 1)))
            print()

            return feedback_lines

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def why_did_opponent_make_this_move(board, current_color, castling_info, move_history, player, initial_castling_info):

        try:

            feedback_sentences = []

            # Move that was actually done by the opponent
            opponent_move = move_history[-1][:-2]

            if opponent_move == [101]:
                opponent_move = [4, 101]
            elif opponent_move == [102]:
                opponent_move = [4, 102]
            elif opponent_move == [103]:
                opponent_move = [60, 103]
            elif opponent_move == [104]:
                opponent_move = [60, 104]
            else:
                opponent_move = [opponent_move[0], opponent_move[2]]

            # Undo a move (as a simulation)
            if True:
                new_board = board[:]
                new_move_history = deepcopy(move_history)

                undo_a_move(new_board, new_move_history)

                if not new_move_history == []:
                    new_castling_info = new_move_history[-1][-1][:]
                else:
                    new_castling_info = initial_castling_info[:]

            feedback_sentences = justify_best_move(feedback_sentences, new_board, not current_color, new_castling_info, new_move_history, player, 0, opponent_move)

            return feedback_sentences

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def what_move_should_i_make(board, current_color, castling_info, move_history, player):

        try:

            feedback_sentences = []

            feedback_sentences = justify_best_move(feedback_sentences, board, current_color, castling_info, move_history, player, 1, None)

            return feedback_sentences

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def was_that_a_strong_move(board, current_color, castling_info, move_histor, player, initial_castling_info):
        
        try:

            feedback_sentences = []

            # Move that was actually done by the opponent
            player_move = move_history[-1][:-2]

            if player_move == [101]:
                player_move = [4, 101]
            elif player_move == [102]:
                player_move = [4, 102]
            elif player_move == [103]:
                player_move = [60, 103]
            elif player_move == [104]:
                player_move = [60, 104]
            else:
                player_move = [player_move[0], player_move[2]]

            # Undo a move (as a simulation)
            if True:
                new_board = board[:]
                new_move_history = deepcopy(move_history)

                undo_a_move(new_board, new_move_history)

                if not new_move_history == []:
                    new_castling_info = new_move_history[-1][-1][:]
                else:
                    new_castling_info = initial_castling_info[:]

            # Run Minimax
            if True:
                # Retrieve the depth from the depth profile
                max_depth = get_depth_from_depth_profile(new_board)

                moves = generate_evaluation_scores_for_every_legal_move_with_multiprocessed_minimax(max_depth, new_board, current_color, new_castling_info, new_move_history)

                print(moves)

                best_evaluation_score = moves[0][0]
                worst_evaluation_score = moves[-1][0]
                range = best_evaluation_score - worst_evaluation_score

            for move in moves:
                if move[1:] == player_move:
                    actual_evaluation_score = move[0]
                    break

            critical_value = best_evaluation_score - 0.05 * range # Move is "alright, bbut not the best" if its evaluation score is within the 5% of the evaluation score range from the best possible evaluation score

            if len(moves) == 1:
                feedback_sentences.append("Honestly, it was the only legal move you could make, so you did't really have any choice.")

            elif range == 0:
                feedback_sentences.append('Yes, I suppose at this point of the game any move would be a decent move.')

            elif actual_evaluation_score == best_evaluation_score:
                feedback_sentences.append('Wow, ' + player[current_color] + ', your move was great!')
                if not moves[1][0] == best_evaluation_score:
                    feedback_sentences.append('In fact, I think it was the best move you could have made!')
                else:
                    feedback_sentences.append('This move is definitely one of the best moves that I could think of.')
            elif (current_color == True and actual_evaluation_score > critical_value) or (current_color == False and actual_evaluation_score < critical_value):
                feedback_sentences.append("It's alright, but I think that there was a better move.")
            else:
                feedback_sentences.append('Not really, I think that there were better moves that you could think of.')

            return feedback_sentences

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def what_other_move_could_i_make(board, current_color, castling_info, move_history, player, initial_castling_info):
        
        try:

            feedback_sentences = []

            # Move that was actually done by the player
            player_move = move_history[-1][:-2]

            if player_move == [101]:
                player_move = [4, 101]
            elif player_move == [102]:
                player_move = [4, 102]
            elif player_move == [103]:
                player_move = [60, 103]
            elif player_move == [104]:
                player_move = [60, 104]
            else:
                player_move = [player_move[0], player_move[2]]

            # Undo a move (as a simulation)
            if True:
                new_board = board[:]
                new_move_history = deepcopy(move_history)

                undo_a_move(new_board, new_move_history)

                if not new_move_history == []:
                    new_castling_info = new_move_history[-1][-1][:]
                else:
                    new_castling_info = initial_castling_info[:]

            feedback_sentences = justify_best_move(feedback_sentences, new_board, current_color, new_castling_info, new_move_history, player, 3, player_move)

            return feedback_sentences

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    def castling_legal_in(moves, castling_code):

        # True if one of the moves is a specified type of castling

        try:

            for move in moves:
                if move[2] == castling_code:
                    return True
            return False

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)
            
    def justify_best_move(feedback_sentences, board, current_color, castling_info, move_history, player, feedback_type, actual_move):

        try:

            # Feedback types:
            # 0. Why did {name} make this move?
            # 1. What move should I make?
            # 2. Was that a strong move? (this subroutine is not called for this feedback type)
            # 3. What other move could I make?

            if True:

                # Retrieve the depth from the depth profile
                max_depth = get_depth_from_depth_profile(board)

                moves = generate_evaluation_scores_for_every_legal_move_with_multiprocessed_minimax(max_depth, board, current_color, castling_info, move_history)

                # Pre-feedback actions & sentences
                if True:
                    if feedback_type == 0:

                        # If the actual move is not at the front of the list, move it to the front (swap with the item with index 0)
                        if not moves[0][1:] == actual_move:
                            for n, move in enumerate(moves):
                                if move[1:] == actual_move:
                                    moves[n] = moves[0]
                                    moves[0] = [moves[0][0], actual_move[0], actual_move[1]] # keep the same evaluation score
                                    break

                    elif feedback_type == 1:
                        pass # nothing here
                    elif feedback_type == 3:
                    
                        best_evaluation_score = moves[0][0]
                        worst_evaluation_score = moves[-1][0]
                        range = best_evaluation_score - worst_evaluation_score

                        for move in moves:
                            if move[1:] == actual_move:
                                actual_evaluation_score = move[0]
                                break

                        if len(moves) == 1:
                            feedback_sentences.append('This was the only move you could have made.')
                            return feedback_sentences

                        elif range == 0:
                            feedback_sentences.append('Honestly, no other move would make any difference.')
                            return feedback_sentences

                        elif actual_evaluation_score == best_evaluation_score:
                            if not moves[1][0] == best_evaluation_score:
                                feedback_sentences.append('Your move already seems to be the best one.')
                                return feedback_sentences
                            else:
                                feedback_sentences.append('Your move already seems to be one of the best ones.')
                                feedback_sentences.append('Another move, which would be just as goos as yours, would be to: ') # COMPLETE THIS

                                # If the actual move is  at the front of the list, swap it with the item with index 1
                                if moves[0][1:] == actual_move:
                                    moves[0] = moves[1]
                                    moves[1] = [moves[0][0], actual_move[0], actual_move[1]]

                        else:
                            pass # proceed to fedback generation

                    pass

                look_at_worse_moves = True

                for n, move in enumerate(moves):

                    # Best move
                    if n == 0:
                        
                        best_move_evaluation_score = move[0]

                        # If an opponent will inevitably checkmate you in the future:
                        if True:
                            if current_color == True and (best_move_evaluation_score - max_depth) <= -1999: # White

                                if int((1999 + best_move_evaluation_score) / 2) == 1:
                                    if feedback_type == 0:
                                        feedback_sentences.append(player[current_color] + ' will be in checkmate in 1 move.')
                                    elif feedback_type == 1:
                                        feedback_sentences.append('Ooops, there is an inevitable checkmate in 1 move.')
                                    elif feedback_type == 3:
                                        feedback_sentences.append('There is an inevitable checkmate in 1 move.')
                                else:
                                    if feedback_type == 0:
                                        feedback_sentences.append(player[current_color] + ' will be in checkmate in {} moves.'.format(str(int((1999 + best_move_evaluation_score) / 2))))
                                    elif feedback_type == 1:
                                        feedback_sentences.append('Ooops, there is an inevitable checkmate in {} moves.'.format(str(int((1999 + best_move_evaluation_score) / 2))))
                                    elif feedback_type == 3:
                                        feedback_sentences.append('There is an inevitable checkmate in {} moves.'.format(str(int((1999 + best_move_evaluation_score) / 2))))

                                if feedback_type == 0:
                                    feedback_sentences.append('There is nothing ' + player[current_color] + ' could do to stop it.')
                                elif feedback_type == 1:
                                    feedback_sentences.append('There is no point in doing anything, you might as well give up.')
                                elif feedback_type == 3:
                                    feedback_sentences.append('Nothing can be done to prevent it.')

                                return feedback_sentences

                            elif current_color == False and (best_move_evaluation_score + max_depth) >= 1999: # Black

                                if int((1999 - best_move_evaluation_score) / 2) == 1:
                                    if feedback_type == 0:
                                        feedback_sentences.append(player[current_color] + ' will be in checkmate in 1 move.')
                                    elif feedback_type == 1:
                                        feedback_sentences.append('Ooops, there is an inevitable checkmate in 1 move.')
                                    elif feedback_type == 3:
                                        feedback_sentences.append('There is an inevitable checkmate in 1 move.')

                                else:
                                    if feedback_type == 0:
                                        feedback_sentences.append(player[current_color] + ' will be in checkmate in {} moves.'.format(str(int((1999 - best_move_evaluation_score) / 2))))
                                    elif feedback_type == 1:
                                        feedback_sentences.append('Ooops, there is an inevitable checkmate in {} moves.'.format(str(int((1999 - best_move_evaluation_score) / 2))))
                                    elif feedback_type == 3:
                                        feedback_sentences.append('There is an inevitable checkmate in {} moves.'.format(str(int((1999 - best_move_evaluation_score) / 2))))

                                if feedback_type == 0:
                                    feedback_sentences.append('There is nothing ' + player[current_color] + ' could do to stop it.')
                                elif feedback_type == 1:
                                    feedback_sentences.append('There is no point in doing anything, you might as well give up.')
                                elif feedback_type == 3:
                                    feedback_sentences.append('Nothing can be done to prevent it.')

                                return feedback_sentences

                        king_position = find_king_position(board, current_color)
                        king_was_under_attack_before_best_move = piece_under_attack(board, None, None, king_position, current_color, False)

                        new_board = board[:]
                        new_castling_info = castling_info[:]
                        new_move_history = deepcopy(move_history)

                        best_move_current_position = move[1]
                        best_move_new_position = move[2]

                        # Remember the piece captured in the best possible move
                        if not best_move_new_position in [101, 102, 103, 104]:
                            best_move_captured_piece = new_board[best_move_new_position]
                        else:
                            best_move_captured_piece = '-'
                        
                        # Remember if the piece was under attack before it was moved
                        if not best_move_new_position in [101, 102, 103, 104]:
                            moved_piece_was_under_attack = piece_under_attack(new_board, None, None, best_move_current_position, current_color, False)
                        else:
                            moved_piece_was_under_attack = False

                        # Simulate the best move
                        make_move(new_board, best_move_current_position, best_move_new_position, new_castling_info, new_move_history, False) # simulates a move, but modifies the copy of a move history and castling info
                        board_after_best_move = new_board[:]
                        best_move = new_move_history[-1][:-2]

                        game_outcome = calculate_game_outcome(new_board, not current_color, new_castling_info)
    
                        # Checkmate caused by the best move
                        if game_outcome in [-1, 1]:
                            
                            if player[not current_color] == 'Computer':

                                if feedback_type == 0:
                                    pass # this combination is impossible
                                elif feedback_type == 1:
                                    feedback_sentences.append('Checkmate the Computer and win the game by ' + write_move(best_move, tense = 'present progressive', lower_case = False)[:-1] + '!')
                                elif feedback_type == 3:
                                    feedback_sentences.append('You could checkmate the Computer and win the game by ' + write_move(best_move, tense = 'present progressive', lower_case = False)[:-1] + '!')

                            else:

                                if feedback_type == 0:
                                    pass # this combination is impossible
                                elif feedback_type == 1:
                                    feedback_sentences.append('Checkmate ' + player[not current_color] + ' and win the game by ' + write_move(best_move, tense = 'present progressive', lower_case = False)[:-1] + '!')
                                elif feedback_type == 3:
                                    feedback_sentences.append('You could checkmate ' + player[not current_color] + ' and win the game by ' + write_move(best_move, tense = 'present progressive', lower_case = False)[:-1] + '!')

                            break
                        
                        # Stalemate caused by the best move (Opponent has no legal moves, but no checkmate)
                        elif game_outcome == 2:

                            if feedback_type == 0:
                                pass # this combination is impossible
                            elif feedback_type == 1:
                                feedback_sentences.append('Cause a Stalemate by ' + write_move(best_move, tense = 'present progressive', lower_case = False))
                                if player[not current_color] == 'Computer':
                                    feedback_sentences.append('A stalemate is still better than losing to the Computer.')
                                else:
                                    feedback_sentences.append('A stalemate is still better than losing to ' + player[not current_color] + '.')
                                break
                            elif feedback_type == 3:
                                feedback_sentences.append('You could cause a Stalemate by ' + write_move(best_move, tense = 'present progressive', lower_case = False))
                                if player[not current_color] == 'Computer':
                                    feedback_sentences.append('A stalemate is still better than losing to the Computer.')
                                else:
                                    feedback_sentences.append('A stalemate is still better than losing to ' + player[not current_color] + '.')
                                break

                        # Continue simulation after the best move
                        elif game_outcome == 0:

                            # Remember if the piece is under attack after it was moved (in the best possible move)
                            if True:
                                if not best_move_new_position in [101, 102, 103, 104]:
                                    moved_piece_is_under_attack = piece_under_attack(new_board, None, None, best_move_new_position, current_color, False)
                                else:
                                    moved_piece_is_under_attack = False

                            # Opponent response move
                            if True:
                                best_scenario_opponent_complete_legal_move_list = create_legal_move_list_for_ALL_pieces(new_board, not current_color, new_castling_info)
                                opponent_current_position, opponent_new_position, opponent_evaluation_score = multiprocessed_minimax_depth_ZERO(max_depth, new_board, (not current_color), new_castling_info, new_move_history)
                            
                                # Remember the piece the opponent captures as a response to the best possible move
                                if not opponent_new_position in [101, 102, 103, 104]:
                                    best_scenario_opponent_captured_piece = new_board[opponent_new_position]
                                else:
                                    best_scenario_opponent_captured_piece = '-'

                                make_move(new_board, opponent_current_position, opponent_new_position, new_castling_info, new_move_history, False) # simulates a move, but modifies the copy of a move history and castling info
                                best_scenario_opponent_move = new_move_history[-1][:-2]

                            # Append feedback sentences (Best move)
                            if True:
                                
                                # If during the previous move the opponent captured any piece (apart from a Pawn) and the best possibble move also captures any piece (apart from a Pawn)
                                # Encourage to complete an exchange
                                if (not move_history == []) and (not move_history[-1][2] in [101, 102, 103, 104]) and (not move_history[-1][3] == '-') and (not best_move_captured_piece == '-'):
                                    best_move_exchange_performed = False
                                    
                                    if feedback_type == 0:
                                        feedback_sentences.append('You captured ' + player[current_color] + "'s " + write_piece_name(move_history[-1][3]) + '.')
                                        feedback_sentences.append('Therefore, ' + player[current_color] + ' completed an exchange by ' + write_move(best_move, tense = 'present progressive', lower_case = True))
                                    elif feedback_type == 1:
                                       feedback_sentences.append('You should complete an exchange by ' + write_move(best_move, tense = 'present progressive', lower_case = True))
                                    elif feedback_type == 3:
                                        feedback_sentences.append('You could complete an exchange by ' + write_move(best_move, tense = 'present progressive', lower_case = True))

                                    look_at_worse_moves = False

                                # If the best possible move captures any piece (apart from a Pawn) and an opponent response move also captures any piece (apart from a Pawn):
                                # Encourage an exchange
                                elif (not best_move_captured_piece == '-') and (not best_scenario_opponent_captured_piece == '-'):
                                    best_move_exchange_performed = True

                                    if feedback_type == 0:
                                        feedback_sentences.append(player[current_color] + ' is exchanging a ' + write_piece_name(best_scenario_opponent_captured_piece) + ' for your ' + write_piece_name(best_move_captured_piece) + '.')
                                    elif feedback_type == 1:
                                        feedback_sentences.append('You would be better off ' + write_exchange_move('you', player[not current_color], best_scenario_opponent_captured_piece, best_move, tense = 'present progressive', lower_case = True))
                                    elif feedback_type == 3:
                                        feedback_sentences.append('You could ' + write_exchange_move('you', player[not current_color], best_scenario_opponent_captured_piece, best_move, tense = 'present progressive', lower_case = True))

                                # If the moved piece was under attack, but was no longer under attack after the best move (But not the king)
                                # Save the piece
                                elif moved_piece_was_under_attack and not moved_piece_is_under_attack and not board_after_best_move[best_move_new_position] in ['k', 'K']:
                                    best_move_exchange_performed = False
                                    
                                    piece_name = board_after_best_move[best_move_new_position]
                                   
                                    if not piece_name in ['k', 'K']:

                                        if feedback_type == 0:
                                            feedback_sentences.append(player[current_color] + "'s " + write_piece_name(piece_name) + ' was under attack.')
                                            sentence = ('Therefore, ' + player[current_color] + ' saved it by ')
                                        elif feedback_type == 1:
                                           sentence = ('Your ' + write_piece_name(piece_name) + ' is under attack. Save it by ')
                                        elif feedback_type == 3:
                                            sentence = ('Your ' + write_piece_name(piece_name) + ' was under attack. You could save it by ')

                                        # If the best move causes a check, write about it
                                        opponent_king_position = find_king_position(board_after_best_move, not current_color)
                                        if piece_under_attack(board_after_best_move, None, None, opponent_king_position, not current_color, False):

                                            if feedback_type == 0:
                                                sentence += ('checking you by ')
                                            elif feedback_type == 1:
                                               sentence += ('checking ' + player[not current_color] + ' by ')
                                            elif feedback_type == 3:
                                                sentence += ('checking ' + player[not current_color] + ' by ')

                                        if feedback_type == 0:
                                            feedback_sentences.append(sentence + write_move(best_move, tense = 'present progressive', lower_case = True))
                                        elif feedback_type == 1:
                                           feedback_sentences.append(sentence + write_move(best_move, tense = 'present progressive', lower_case = True))
                                        elif feedback_type == 3:
                                            feedback_sentences.append(sentence + write_move(best_move, tense = 'present progressive', lower_case = True))

                                    return feedback_sentences

                                # If your King was in check
                                # Suggest to get out of check
                                elif king_was_under_attack_before_best_move:

                                    if True:
                                      
                                        if feedback_type == 0:
                                            feedback_sentences.append(player[current_color] + "'s King was in check.")
                                            feedback_sentences.append('To get out of check, ' + player[current_color] + ' had to ' + write_move(best_move, tense = 'present', lower_case = True))
                                        elif feedback_type == 1:
                                           feedback_sentences.append('Your King is in check. To get out of check, you should ' + write_move(best_move, tense = 'present', lower_case = True))
                                        elif feedback_type == 3:
                                            feedback_sentences.append('Your King was in check. To get out of check, you could ' + write_move(best_move, tense = 'present', lower_case = True))

                                    return feedback_sentences

                                # No exchange and moved piece didn't need saving:
                                else:
                                    best_move_exchange_performed = False
                                    
                                    sentence = ''

                                    # If the best move causes a check, write about it
                                    opponent_king_position = find_king_position(board_after_best_move, not current_color)
                                    if piece_under_attack(board_after_best_move, None, None, opponent_king_position, not current_color, False):

                                        if feedback_type == 0:
                                            sentence += (player[current_color] + ' checked your King ')
                                        elif feedback_type == 1:
                                           sentence += ('You should check ' + player[not current_color] + ' ')
                                        elif feedback_type == 3:
                                            sentence += ('You could check ' + player[not current_color] + ' ')

                                    # I need this conversion for the new position to generate an attack list
                                    if best_move_new_position == 101:
                                        actual_new_position = 2
                                    elif best_move_new_position == 102:
                                        actual_new_position = 6
                                    elif best_move_new_position == 103:
                                        actual_new_position = 58
                                    elif best_move_new_position == 104:
                                        actual_new_position = 62
                                    else:
                                        actual_new_position = best_move_new_position

                                    # If the moved piece attacks any of the opponent's pieces after the best move:
                                    # Write about it in order from the most important piece to least important piece,
                                    # Ignore Pawns
                                    # Ignore if the piece under attack is not more important than the captured piece
                                    current_player_attack_list = create_attack_list(board_after_best_move, actual_new_position, current_color, new_castling_info, None)
                                    first_attack = True
                                    for attacked_piece in current_player_attack_list:
                                        if best_move_captured_piece == '-' or (not best_move_captured_piece == '-' and piece_is_more_significant(attacked_piece, best_move_captured_piece)):
                                            if sentence == '':

                                                if feedback_type == 0:
                                                    sentence += (player[current_color] + ' attacked your ')
                                                elif feedback_type == 1:
                                                   sentence += ('You should attack ' + player[not current_color] + "'s ")
                                                elif feedback_type == 3:
                                                    sentence += ('You could attack ' + player[not current_color] + "'s ")

                                                first_attack = False
                                            elif first_attack:

                                                if feedback_type == 0:
                                                    sentence += ('and attacked your ')
                                                elif feedback_type == 1:
                                                   sentence += ('and attack ' + player[not current_color] + "'s ")
                                                elif feedback_type == 3:
                                                    sentence += ('and attack ' + player[not current_color] + "'s ")

                                                first_attack = False
                                            else:

                                                if feedback_type == 0:
                                                    sentence += ('and ')
                                                elif feedback_type == 1:
                                                    sentence += ('and ')
                                                elif feedback_type == 3:
                                                    sentence += ('and ')

                                            if feedback_type == 0:
                                                sentence += (write_piece_name(attacked_piece) + ' ')
                                            elif feedback_type == 1:
                                                sentence += (write_piece_name(attacked_piece) + ' ')
                                            elif feedback_type == 3:
                                                sentence += (write_piece_name(attacked_piece) + ' ')

                                    if not sentence == '':

                                        if feedback_type == 0:
                                            feedback_sentences.append(sentence + 'by ' + write_move(best_move, tense = 'present progressive', lower_case = True))
                                        elif feedback_type == 1:
                                            feedback_sentences.append(sentence + 'by ' + write_move(best_move, tense = 'present progressive', lower_case = True))
                                        elif feedback_type == 3:
                                            feedback_sentences.append(sentence + 'by ' + write_move(best_move, tense = 'present progressive', lower_case = True))

                                    else:

                                        if feedback_type == 0:
                                            feedback_sentences.append(player[current_color] + ' ' + write_move(best_move, tense = 'past', lower_case = True))
                                        elif feedback_type == 1:
                                            feedback_sentences.append(write_move(best_move, tense = 'present', lower_case = False))
                                        elif feedback_type == 3:
                                            feedback_sentences.append('You could ' + write_move(best_move, tense = 'present', lower_case = True))

                                    # Justification of castling
                                    if best_move_new_position in [101, 102, 103, 104]:

                                        if feedback_type == 0:
                                            feedback_sentences.append('It provides better protection for ' + player[current_color] + "'s King and moves a Rook to a better position on the board.")
                                        elif feedback_type == 1:
                                            feedback_sentences.append('It would protect your King and move your Rook to a better position on the board.')
                                        elif feedback_type == 3:
                                            feedback_sentences.append('It would protect your King and move your Rook to a better position on the board.')

                                # If the best move leads the player to an inevitable checkmate (WIN)
                                if True:
                                    if current_color == False and (opponent_evaluation_score - max_depth) <= -1999: # Black

                                        if int((1999 + opponent_evaluation_score) / 2) == 1:

                                            if feedback_type == 0:
                                                feedback_sentences.append('This move allows ' + player[current_color] + ' to checkmate you within one move regardless of what you do!')
                                            elif feedback_type == 1:
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('If you make this move, you will be able to checkmate the Computer and win the game next move!')
                                                else:
                                                    feedback_sentences.append('If you make this move, you will be able to checkmate ' + player[not current_color] + ' and win the game next move!')
                                            elif feedback_type == 3:
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('If you made this move, you would be able to checkmate the Computer and win the game next move!')
                                                else:
                                                    feedback_sentences.append('If you made this move, you would be able to checkmate ' + player[not current_color] + ' and win the game next move!')

                                        else:

                                            if feedback_type == 0:
                                                feedback_sentences.append('This move allows ' + player[current_color] + ' to checkmate you within {} moves regardless of what you do!'.format(str(int((1999 + opponent_evaluation_score) / 2))))
                                            elif feedback_type == 1:
                                                feedback_sentences.append('This move will lead you onto an ultimate path of winning.')
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('You will be able to checkmate the Computer in {} moves!'.format(str(int((1999 + opponent_evaluation_score) / 2))))
                                                else:
                                                    feedback_sentences.append('You will be able to checkmate ' + player[not current_color] + ' in {} moves!'.format(str(int((1999 + opponent_evaluation_score) / 2))))
                                            elif feedback_type == 3:
                                                feedback_sentences.append('This move could lead you onto an ultimate path of winning.')
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('You would be able to checkmate the Computer in {} moves!'.format(str(int((1999 + opponent_evaluation_score) / 2))))
                                                else:
                                                    feedback_sentences.append('You would be able to checkmate ' + player[not current_color] + ' in {} moves!'.format(str(int((1999 + opponent_evaluation_score) / 2))))

                                        return feedback_sentences

                                    elif current_color == True and (opponent_evaluation_score + max_depth) >= 1999: # White

                                        if int((1999 - opponent_evaluation_score) / 2) == 1:

                                            if feedback_type == 0:
                                                feedback_sentences.append('This move allows ' + player[current_color] + ' to checkmate you within one move regardless of what you do!')
                                            elif feedback_type == 1:
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('If you make this move, you will be able to Checkmate the Computer and win the game next move!')
                                                else:
                                                    feedback_sentences.append('If you make this move, you will be able to Checkmate ' + player[not current_color] + ' and win the game next move!')
                                            elif feedback_type == 3:
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('If you made this move, you would be able to checkmate the Computer and win the game next move!')
                                                else:
                                                    feedback_sentences.append('If you made this move, you would be able to checkmate ' + player[not current_color] + ' and win the game next move!')

                                        else:

                                            if feedback_type == 0:
                                                feedback_sentences.append('This move allows ' + player[current_color] + ' to checkmate you within {} moves regardless of what you do!'.format(str(int((1999 - opponent_evaluation_score) / 2))))
                                            elif feedback_type == 1:
                                                feedback_sentences.append('This move will lead you onto an ultimate path of winning.')
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('You will be able to checkmate the Computer in {} moves!'.format(str(int((1999 - opponent_evaluation_score) / 2))))
                                                else:
                                                    feedback_sentences.append('You will be able to checkmate ' + player[not current_color] + ' in {} moves!'.format(str(int((1999 - opponent_evaluation_score) / 2))))
                                            elif feedback_type == 3:
                                                feedback_sentences.append('This move could lead you onto an ultimate path of winning.')
                                                if player[not current_color] == 'Computer':
                                                    feedback_sentences.append('You would be able to checkmate the Computer in {} moves!'.format(str(int((1999 - opponent_evaluation_score) / 2))))
                                                else:
                                                    feedback_sentences.append('You would be able to checkmate ' + player[not current_color] + ' in {} moves!'.format(str(int((1999 - opponent_evaluation_score) / 2))))
                                                    # CONTIUE HERE
                                        return feedback_sentences

                            # Player response move
                            if True:
                                player_response_current_position, player_response_new_position, player_response_evaluation_score = multiprocessed_minimax_depth_ZERO(max_depth, new_board, current_color, new_castling_info, new_move_history)

                                # Remember the piece the player captures as a response to the opponent's response move
                                if not player_response_new_position in [101, 102, 103, 104]:
                                    best_scenario_player_response_captured_piece = new_board[player_response_new_position]
                                else:
                                    best_scenario_player_response_captured_piece = '-'

                                make_move(new_board, player_response_current_position, player_response_new_position, new_castling_info, new_move_history, False) # simulates a move, but modifies the copy of a move history and castling info
                                player_response_move = new_move_history[-1][:-2]

                            # Append feedback sentences (What it would allow you to do in the future)
                            if True:

                                # If exchange hasn't yet been performed and the opponent response move captures any piece (apart from a Pawn) and the player response move also captures any piece (apart from a Pawn):
                                # Say that it will allow yoou to exchange ....
                                # Exchange:
                                if (not best_move_exchange_performed) and (not best_scenario_opponent_captured_piece == '-') and (not best_scenario_player_response_captured_piece == '-'):

                                    if feedback_type == 0:
                                        feedback_sentences.append(player[current_color] + ' probably expects you to ' + write_move(best_scenario_opponent_move, tense = 'present', lower_case = True))
                                        feedback_sentences.append('It will let ' + player[current_color] + ' ' + write_exchange_move('a', 'you', best_scenario_opponent_captured_piece, player_response_move, tense = 'present', lower_case = True))
                                    elif feedback_type == 1:
                                        feedback_sentences.append(player[not current_color] + ' will then probably ' + write_move(best_scenario_opponent_move, tense = 'present', lower_case = True))
                                        feedback_sentences.append('It will let you ' + write_exchange_move('you', player[not current_color], best_scenario_opponent_captured_piece, player_response_move, tense = 'present', lower_case = True))
                                    elif feedback_type == 3:
                                        feedback_sentences.append(player[not current_color] + ' would then probably ' + write_move(best_scenario_opponent_move, tense = 'present', lower_case = True))
                                        feedback_sentences.append('It would let you ' + write_exchange_move('you', player[not current_color], best_scenario_opponent_captured_piece, player_response_move, tense = 'present', lower_case = True))

                                else:

                                    deep_exchange = False

                                    # If exchange hasn't yet been performed and the opponent response move doesn't capture any pieces, but the player response move captures any piece (apart from a Pawn):
                                    # Simulate a deeper opponent response move to see if it is an exchange
                                    if (not best_move_exchange_performed) and (not best_scenario_player_response_captured_piece in ['-']):
                                    
                                        # Deep opponent response move
                                        if True:
                                            deep_opponent_current_position, deep_opponent_new_position, deep_opponent_evaluation_score = multiprocessed_minimax_depth_ZERO(max_depth - 1, new_board, (not current_color), new_castling_info, new_move_history)

                                            # Remember the piece the opponent captures in a deep response move
                                            if not deep_opponent_new_position in [101, 102, 103, 104]:
                                                best_scenario_deep_opponent_captured_piece = new_board[deep_opponent_new_position]
                                            else:
                                                best_scenario_deep_opponent_captured_piece = '-'

                                            # No need to make the deep opponent response move (no need to call the make_move function)
                                            # Therefore new_board, new_castling_info and new_move_history do not change

                                        if not best_scenario_deep_opponent_captured_piece in ['-']:
                                            deep_exchange = True

                                            if feedback_type == 0:
                                                feedback_sentences.append(player[current_color] + ' probably expects you to ' + write_move(best_scenario_opponent_move, tense = 'present', lower_case = True))
                                                feedback_sentences.append(player[current_color] + ' will then be able to ' + write_exchange_move('a', 'you', best_scenario_deep_opponent_captured_piece, player_response_move, tense = 'present', lower_case = True))
                                            elif feedback_type == 1:
                                                feedback_sentences.append(player[not current_color] + ' will then probably ' + write_move(best_scenario_opponent_move, tense = 'present', lower_case = True))
                                                feedback_sentences.append('You will then be able to ' + write_exchange_move('you', player[not current_color], best_scenario_deep_opponent_captured_piece, player_response_move, tense = 'present', lower_case = True))
                                            elif feedback_type == 3:
                                                feedback_sentences.append(player[not current_color] + ' would then probably ' + write_move(best_scenario_opponent_move, tense = 'present', lower_case = True))
                                                feedback_sentences.append('You would then be able to ' + write_exchange_move('you', player[not current_color], best_scenario_deep_opponent_captured_piece, player_response_move, tense = 'present', lower_case = True))

                                    # No exchange:
                                    if not deep_exchange:

                                        # If a player response move checks the opponent's King
                                        opponent_king_position = find_king_position(new_board, not current_color)
                                        if piece_under_attack(new_board, None, None, opponent_king_position, not current_color, False):

                                            if feedback_type == 0:
                                                feedback_sentences.append(player[current_color] + ' will later be able to check you by ' + write_move(player_response_move, tense = 'present progressive', lower_case = True))
                                            elif feedback_type == 1:
                                                feedback_sentences.append('You will later be able to check ' + player[not current_color] + ' by ' + write_move(player_response_move, tense = 'present progressive', lower_case = True))
                                            elif feedback_type == 3:
                                                feedback_sentences.append('You would later be able to check ' + player[not current_color] + ' by ' + write_move(player_response_move, tense = 'present progressive', lower_case = True))

                                        # If castling was not avaiable for the original move, but player response move is to castle
                                        elif player_response_move[0] in [101, 102, 103, 104]:
                                            if not castling_legal_in(moves, player_response_move[0]):

                                                if feedback_type == 0:
                                                    feedback_sentences.append('Later on ' + player[current_color] + ' will be able to ' + write_move(player_response_move, tense = 'present', lower_case = True))
                                                elif feedback_type == 1:
                                                    feedback_sentences.append('Later on you will be able to ' + write_move(player_response_move, tense = 'present', lower_case = True))
                                                elif feedback_type == 3:
                                                    feedback_sentences.append('Later on you would be able to ' + write_move(player_response_move, tense = 'present', lower_case = True))

                                        # If the player response move captures an opponent's piece 
                                        # Or player response move promotes a Pawn
                                        elif (not player_response_move[3] == '-') or (player_response_move[1] == 'p' and player_response_move[2] < 8) or (player_response_move[1] == 'P' and player_response_move[2] > 55):

                                            if feedback_type == 0:
                                                feedback_sentences.append('Later on ' + player[current_color] + ' will be able to ' + write_move(player_response_move, tense = 'present', lower_case = True))
                                            elif feedback_type == 1:
                                                feedback_sentences.append('Later on you will be able to ' + write_move(player_response_move, tense = 'present', lower_case = True))
                                            elif feedback_type == 3:
                                                feedback_sentences.append('Later on you would be able to ' + write_move(player_response_move, tense = 'present', lower_case = True))

                    # Worse move (max of 4 worse moves to be considered)                     
                    elif (n < 6 and look_at_worse_moves) or feedback_type == 3:

                        if not feedback_type == 3:
                            player_evaluation_score = move[0]
                        else:
                            player_evaluation_score = actual_evaluation_score

                        # Only consider the worse move if its evaluation score is worse than the evaluation score of the best move (unless feedback_type == 3)
                        if (current_color == True and player_evaluation_score < best_move_evaluation_score) or (current_color == False and player_evaluation_score > best_move_evaluation_score) or feedback_type == 3:

                            if not feedback_type == 3:
                                player_current_position = move[1]
                                player_new_position = move[2]
                            else:
                                player_current_position = actual_move[0]
                                player_new_position = actual_move[1]

                            new_board = board[:]
                            new_castling_info = castling_info[:]
                            new_move_history = deepcopy(move_history)

                            make_move(new_board, player_current_position, player_new_position, new_castling_info, new_move_history, False) # simulates a move, but modifies the copy of a move history and castling info

                            game_outcome = calculate_game_outcome(new_board, not current_color, new_castling_info)

                            if game_outcome == 0: # Game hasn't ended
                                # Now simulates an opponent response move
                            
                                new_color = not current_color

                                opponent_current_position, opponent_new_position, opponent_evaluation_score = multiprocessed_minimax_depth_ZERO(max_depth, new_board, new_color, new_castling_info, new_move_history)
                                make_move(new_board, opponent_current_position, opponent_new_position, new_castling_info, new_move_history, False) # simulates a move, but modifies the copy of a move history and castling info
                                otherwise_opponent_move = new_move_history[-1][:-2]

                                game_outcome = calculate_game_outcome(new_board, current_color, new_castling_info)

                                # Checkmate caused by the best move
                                if game_outcome in [-1, 1]:
                            
                                    if feedback_type == 0:
                                        feedback_sentences.append('By doing so, ' + player[current_color] + 'prevented you from checkmating him by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = False))
                                    elif feedback_type == 1:
                                        feedback_sentences.append('Otherwise, ' + player[not current_color] + ' might Checkmate you by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = False))
                                    elif feedback_type == 3:
                                        feedback_sentences.append('Otherwise, ' + player[not current_color] + ' might Checkmate you by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = False))

                                # Stalemate caused by the best move (Opponent has no legal moves, but no checkmate)
                                elif game_outcome == 2:

                                    if feedback_type == 0:
                                        feedback_sentences.append('By doing so, ' + player[current_color] + 'prevented you from causing a stalemate by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = False))
                                    elif feedback_type == 1:
                                        feedback_sentences.append('Otherwise, ' + player[not current_color] + ' might cause a Stalemate by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = False))
                                    elif feedback_type == 3:
                                        feedback_sentences.append('Otherwise, ' + player[not current_color] + ' might cause a Stalemate by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = False))

                                # Game does not end
                                # Append feedback sentences
                                elif game_outcome == 0:

                                    # 1. If opponent does not capture the player's piece that moved right before it (When a worse move is simulated, it should not be displayed that it is possible to prevent an opponent from capturing a piece that was simulated to move, because in reality in is in a different place on the board)
                                    # (not opponent_new_position == player_new_position)
                                    #  UNLESS (feedback_type == 3)
                                
                                    # 2. If opponent's response is not the same for both the best possible move and a worse move
                                    # (not best_scenario_opponent_move == otherwise_opponent_move)

                                    # 3. If opponent's response move to the worse move is also legal as a response move for the best move
                                    # ([opponent_current_position, opponent_new_position] in best_scenario_opponent_complete_legal_move_list)
                                    #  UNLESS (feedback_type == 3)

                                    # 4. If not (Piece moved by opponent after a worse move is not under attack, but it would be under attack if the same move was to be made after the best possible move)
                                    # (not ((not opponent_new_position in [101, 102, 103, 104]) and not piece_under_attack(new_board, None, None, opponent_new_position, not current_color, False) and piece_under_attack(board_after_best_move, opponent_current_position, opponent_new_position, opponent_new_position, not current_color, True)))
                                    # UNLESS (feedback_type == 3)

                                    if (not opponent_new_position == player_new_position) or feedback_type == 3:
                                        if not best_scenario_opponent_move == otherwise_opponent_move:
                                            if [opponent_current_position, opponent_new_position] in best_scenario_opponent_complete_legal_move_list or feedback_type == 3:
                                                if (not ((not opponent_new_position in [101, 102, 103, 104]) and not piece_under_attack(new_board, None, None, opponent_new_position, not current_color, False) and piece_under_attack(board_after_best_move, opponent_current_position, opponent_new_position, opponent_new_position, not current_color, True))) or feedback_type == 3:
                                                    if True:

                                                        if feedback_type == 0:
                                                            if len(feedback_sentences) == 1: # No feedback points have been made yet (apart from a move suggestion)
                                                                sentence = 'By doing so, ' + player[current_color] + ' probably tries to prevent you from '
                                                            else:
                                                                sentence = 'By doing so, ' + player[current_color] + ' probably also tries to prevent you from '
                                                        elif feedback_type == 1:
                                                            if len(feedback_sentences) == 1: # No feedback points have been made yet (apart from a move suggestion)
                                                                sentence = 'It should prevent ' + player[not current_color] + ' from '
                                                            else:
                                                                sentence = 'It should also prevent ' + player[not current_color] + ' from '
                                                        elif feedback_type == 3:
                                                            sentence = 'It should prevent ' + player[not current_color] + ' from '

                                                        # If opponent chacks the player AND the player hasn't moved the king in the worse move
                                                        current_player_king_position = find_king_position(new_board, current_color)
                                                        if piece_under_attack(new_board, None, None, current_player_king_position, current_color, False) and (board[current_player_king_position] in ['k', 'K']):

                                                            if feedback_type == 0:
                                                                sentence += ('checking ' + player[current_color] + ' ')
                                                            elif feedback_type == 1:
                                                                sentence += ('checking you ')
                                                            elif feedback_type == 3:
                                                                sentence += ('checking you ')

                                                        # I need this conversion for the new position to generate an attack list
                                                        if opponent_new_position == 101:
                                                            actual_new_position = 2
                                                        elif opponent_new_position == 102:
                                                            actual_new_position = 6
                                                        elif opponent_new_position == 103:
                                                            actual_new_position = 58
                                                        elif opponent_new_position == 104:
                                                            actual_new_position = 62
                                                        else:
                                                            actual_new_position = opponent_new_position
                                                            
                                                        # Attack list excludes Kings, Pawns and pieces that would not be on the same position on the board if the best move was made
                                                        opponent_attack_list = create_attack_list(new_board, actual_new_position, not current_color, new_castling_info, board_after_best_move)
                                                        first_attack = True
                                                        for piece in opponent_attack_list:
                                                            if sentence[-6:] == ' from ':

                                                                if feedback_type == 0:
                                                                    sentence += ('attacking ' + player[current_color] + "'s ")
                                                                elif feedback_type == 1:
                                                                    sentence += ('attacking your ')
                                                                elif feedback_type == 3:
                                                                    sentence += ('attacking your ')

                                                                first_attack = False
                                                            elif first_attack:

                                                                if feedback_type == 0:
                                                                    sentence += ('and attacking ' + player[current_color] + "'s ")
                                                                elif feedback_type == 1:
                                                                    sentence += ('and attacking your ')
                                                                elif feedback_type == 3:
                                                                    sentence += ('and attacking your ')

                                                                first_attack = False
                                                            else:

                                                                if feedback_type == 0:
                                                                    sentence += ('and ')
                                                                elif feedback_type == 1:
                                                                    sentence += ('and ')
                                                                elif feedback_type == 3:
                                                                    sentence += ('and ')

                                                            if feedback_type == 0:
                                                                sentence += (write_piece_name(piece) + ' ')
                                                            elif feedback_type == 1:
                                                                sentence += (write_piece_name(piece) + ' ')
                                                            elif feedback_type == 3:
                                                                sentence += (write_piece_name(piece) + ' ')

                                                        if not sentence[-6:] == ' from ':

                                                            if feedback_type == 0:
                                                                feedback_sentences.append(sentence + 'by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))
                                                            elif feedback_type == 1:
                                                                feedback_sentences.append(sentence + 'by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))
                                                            elif feedback_type == 3:
                                                                feedback_sentences.append(sentence + 'by ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))

                                                        else:

                                                            if feedback_type == 0:
                                                                if len(feedback_sentences) == 1: # No feedback points have been made yet (apart from a move suggestion)
                                                                    feedback_sentences.append('By doing so, ' + player[current_color] + ' probably tries to stop you from ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))
                                                                else:
                                                                    feedback_sentences.append('By doing so, ' + player[current_color] + ' probably also tries to stop you from ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))
                                                            elif feedback_type == 1:
                                                                if len(feedback_sentences) == 1: # No feedback points have been made yet (apart from a move suggestion)
                                                                    feedback_sentences.append('It should stop ' + player[not current_color] + ' from ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))
                                                                else:
                                                                    feedback_sentences.append('It should also stop ' + player[not current_color] + ' from ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))
                                                            elif feedback_type == 3:
                                                                feedback_sentences.append('It could stop ' + player[not current_color] + ' from ' + write_move(otherwise_opponent_move, tense = 'present progressive', lower_case = True))

                                                    # If the worse move leads the player to an inevitable checkmate (LOSS)
                                                    if True:
                                                        if current_color == True and (opponent_evaluation_score - max_depth) <= -1999: # White

                                                            if int((1999 + opponent_evaluation_score) / 2) == 1:

                                                                if feedback_type == 0:
                                                                    feedback_sentences.append('If ' + player[current_color] + ' let you make this move, you could win within one move.')
                                                                elif feedback_type == 1:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you next move!')
                                                                elif feedback_type == 3:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you next move!')

                                                            else:

                                                                if feedback_type == 0:
                                                                    feedback_sentences.append('If ' + player[current_color] + ' let you make this move, you could win within {} moves.'.format(str(int((1999 + opponent_evaluation_score) / 2))))
                                                                elif feedback_type == 1:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you in ' + str(int((1999 + opponent_evaluation_score) / 2)) + ' moves!')
                                                                elif feedback_type == 3:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you in ' + str(int((1999 + opponent_evaluation_score) / 2)) + ' moves!')

                                                        elif current_color == False and (opponent_evaluation_score + max_depth) >= 1999: # Black

                                                            if int((1999 - opponent_evaluation_score) / 2) == 1:

                                                                if feedback_type == 0:
                                                                    feedback_sentences.append('If ' + player[current_color] + ' let you make this move, you could win within one move.')
                                                                elif feedback_type == 1:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you next move!')
                                                                elif feedback_type == 3:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you next move!')

                                                            else:

                                                                if feedback_type == 0:
                                                                    feedback_sentences.append('If ' + player[current_color] + ' let you make this move, you could win within {} moves.'.format(str(int((1999 - opponent_evaluation_score) / 2))))
                                                                elif feedback_type == 1:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you in ' + str(int((1999 + opponent_evaluation_score) / 2)) + ' moves!')
                                                                elif feedback_type == 3:
                                                                    feedback_sentences.append('If you let ' + player[not current_color] + ' make this move, ' + player[not current_color] + ' might Checkmate you in ' + str(int((1999 + opponent_evaluation_score) / 2)) + ' moves!')

                                                    return feedback_sentences

                        if feedback_type == 3:
                            break

            # Just in case if computer fails to come up with a reasonable explanation:
            if len(feedback_sentences) == 1 and look_at_worse_moves:
                if feedback_type == 0:
                    feedback_sentences.append(player[current_color] + ' probably thinks that this is a better strategic position for ' + player[current_color] + "'s " + write_piece_name(best_move[1]) + '.')
                elif feedback_type == 1:
                    feedback_sentences.append('This is a better strategic position for your ' + write_piece_name(best_move[1]) + '.')
                elif feedback_type == 3:
                    feedback_sentences.append('This would be a better strategic position for your ' + write_piece_name(best_move[1]) + '.')

            return feedback_sentences

        except Exception as e:
            function_name = inspect.currentframe().f_code.co_name
            add_exception_to_log(function_name, e)

    pass # Feedback generation

if __name__ == '__main__':

    freeze_support() # to prevent it from opening a bunch of windows when running multiple processes and the py file is converted to an exe file
    board_size = get_board_size()
    cell_size = int(board_size / 8) # width and height of each square on the board in pixels
    gameDisplay = initiate_and_fill_window_and_display_logo(board_size)
    clock = pygame.time.Clock()

    state = 'transition to the welcoming window'
    # States:
    # 'transition to the welcoming window'
    # 'welcoming window'
    # 'setup window'
    # 'new game'
    # 'next player'
    # 'waiting for 1st click' - waits for user to select the piece to move
    # 'waiting for 2nd click' - waits for user to select the destination cell for the piece
    # 'transition to human player moved'
    # 'human player moved'
    # 'game over'

    # Main frame loop
    while True:

        # States
        if True:
            if state == 'transition to the welcoming window':
                # Sets up a board so that an initial game setup would be shown in the welcoming window
                board, castling_info, current_color, player = get_a_game_scenario('Classic')

                current_position = None
                computer_current_position = None
                computer_new_position = None
                legal_move_list = []
                upside_down = False

                state = 'welcoming window'
                play_against_a_computer_button_is_selected = False
                play_against_a_human_button_is_selected = False
                play_a_game_scenario_is_selected = False
                see_the_game_history_button_is_selected = False
                minus_button_is_selected = False
                plus_button_is_selected = False
                go_back_button_is_selected = False

            elif state == 'setup window human vs computer':
                go_back, board, initial_castling_info, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black = setup_human_vs_computer(board_size)
            
                if go_back:
                    state = 'transition to the welcoming window'
                    current_position = None
                    upside_down = False
                    legal_move_list = []
                else:
                    state = 'new game'

            elif state == 'setup window human vs human':
                go_back, board, initial_castling_info, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black = setup_human_vs_human(board_size)
            
                if go_back:
                    state = 'transition to the welcoming window'
                    current_position = None
                    upside_down = False
                    legal_move_list = []
                else:
                    state = 'new game'

            elif state == 'select a game scenario':
                decision, board, initial_castling_info, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black = scenario_selection_window(board_size)

                if decision == 'Go back':
                    state = 'transition to the welcoming window'
                    current_position = None
                    upside_down = False
                    legal_move_list = []
                elif decision == 'Play':
                    state = 'new game'
                else: # decision == 'Create scenario'
                    state = 'creating a scenario, waiting for 1st click'

            elif state == 'new game':
                current_position = None
                legal_move_list = []
                upside_down = False
                move_history = [] # [[old_pos, selected_piece, new_pos, captured_piece, captured_pieces, castling_info], []] A player moves a selected_piece and captures a captured_piece
                move_counter = 0
                white_move_times = []
                black_move_times = []
                computer_move_times = []
                average_time_per_move_white = None
                average_time_per_move_black = None
                average_time_per_move_computer = None

                castling_info = initial_castling_info[:]

                how_are_the_points_calculated_button_is_selected = False
                show_the_move_history_button_is_selected = False
                pass_the_move_over_to_the_opponent_button_is_selected = False

                # Reset the feedback variables
                feedbacks = [None, None, None, None]
                selected_feedback_options = [False, False, False, False]
                what_other_move_could_i_make_first_appearance = True

                if player[True] == 'Computer' and not player[False] == 'Computer':
                    upside_down = True # Board displayed upside down
                else:
                    upside_down = False

                state = 'next player'

            elif state == 'next player':
                
                current_color = not current_color

                # print('Evalution score: {}'.format(evaluate(board, current_color, castling_info, depth = 0)))
                #print()

                if not player[current_color] == 'Computer':

                    current_player = 'human'
                    upside_down = False if current_color == True else True

                else:
                    current_player = 'Computer'

                game_outcome = calculate_game_outcome(board, current_color, castling_info)

                # Game over
                if not game_outcome == 0:
                    if game_outcome in [1, -1]:
                        print('CHECKMATE')
                    elif game_outcome == 2:
                        print('STALEMATE')
                    elif game_outcome == 3:
                        print('DRAW')

                    if len(move_history) > 2:
                        show_undo_button = True
                    else:
                        show_undo_button = False

                    undo_a_move_button_is_selected = game_over_window(game_outcome, player, move_counter, average_time_per_move_white, average_time_per_move_black, show_undo_button, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords)
                    
                    if undo_a_move_button_is_selected:

                        undo_a_move(board, move_history)
                        undo_a_move(board, move_history)

                        if current_color == True:
                            move_counter -= 2
                        else:
                            move_counter -= 1
                                       
                        current_color = not current_color
                        current_position = None # so that there would be no highlighted cells on the board
                        legal_move_list = []

                        how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                        what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                    else:
                        state = 'transition to the welcoming window'
                    
                elif current_player == 'Computer':
                    state = 'turn passed to a computer'
                    pass

                elif current_player == 'human':

                    start_time_human_player = time.time() # Starts the stopwatch to measure the time it takes a user to make a move

                    state = 'waiting for 1st click'
                    forfeit_button_is_selected = False
                    exit_button_is_selected = False
                    flip_the_board_button_is_selected = False
                    undo_a_move_button_is_selected = False
                    
            elif state == 'turn passed to a computer':

                start_time = time.time()

                # Retrieve the depth from the depth profile
                max_depth = get_depth_from_depth_profile(board)

                computer_current_position, computer_new_position, _ = multiprocessed_minimax_depth_ZERO(max_depth, board, current_color, castling_info, move_history)

                end_time = time.time()
                print('Evaluation time: {}s'.format(round(end_time - start_time, 1)))

                computer_move_times.append(round(end_time - start_time, 1))
                average_time_per_move_computer = calculate_average_time_per_move(computer_move_times)
                print('Average time: {}s'.format(average_time_per_move_computer))
                print()

                make_move(board, computer_current_position, computer_new_position, castling_info, move_history, False)

                state = 'computer player moved'

            elif state == 'transition to human player moved':
                state = 'human player moved'

            elif state == 'computer player moved':
                 state = 'next player'
                 pass

            elif state in ['waiting for 1st click', 'waiting for 2nd click']:
                if not time_limit == None:
                    remaining_time = round((time_limit + start_time_human_player - time.time()), 1)
                    if remaining_time <= 0:
                        
                        game_outcome = 5 # reason - ran out of time
                        continue_button_is_selected = game_over_window(game_outcome, player, move_counter, average_time_per_move_white, average_time_per_move_black, False, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords)

                        if continue_button_is_selected:
                            
                            complete_legal_move_list = create_legal_move_list_for_ALL_pieces(board, current_color, castling_info)

                            move = complete_legal_move_list[random.randint(0, (len(complete_legal_move_list) - 1))]

                            current_position = move[0]
                            new_position = move[1]

                            make_move(board, current_position, new_position, castling_info, move_history, False)
                            current_position = None
                            legal_move_list = []
                            state = 'transition to human player moved'

                        else:
                            state = 'transition to the welcoming window'

            elif state == 'human player moved':
                if not time_limit == None: # If human made a move, but has not submitted it on time, submit it automatically
                    remaining_time = round((time_limit + start_time_human_player - time.time()), 1)
                    if remaining_time <= 0:

                        if current_color == True: # White
                            white_move_times.append(time_limit)
                            average_time_per_move_white = calculate_average_time_per_move(white_move_times)
                        else: # current_player == False: # Black
                            black_move_times.append(time_limit)
                            average_time_per_move_black = calculate_average_time_per_move(black_move_times)

                        what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)
                        state = 'next player'

        # Detects events through pygame and goes through them
        for event in pygame.event.get():

            # Quit
            if event.type == pygame.QUIT:
                quit_program() # Quits the program
                pass

            # Clicks
            elif event.type == pygame.MOUSEBUTTONDOWN: # Detects any other mouse clicks
                mouse_coords = pygame.mouse.get_pos()

                computer_current_position = None
                computer_new_position = None

                # Clicks outside the board
                if not (clicked_within_the_board(mouse_coords, board_size) or (state in ['creating a scenario, waiting for 1st click', 'creating a scenario, waiting for 2nd click'] and (clicked_within_the_board(mouse_coords, board_size) or clicked_within_creating_a_scenario_tiles(mouse_coords, board_size)))):

                    if state == 'waiting for 2nd click':
                        current_position = None
                        legal_move_list = []
                        state = 'waiting for 1st click'
                    elif state == 'creating a scenario, waiting for 2nd click':
                        current_position = None
                        legal_move_list = []
                        state = 'creating a scenario, waiting for 1st click'
                    else:
                        x_coord = mouse_coords[0]
                        y_coord = mouse_coords[1]

                        if state == 'welcoming window':
                            if int(2.225 * board_size) < x_coord < int(2.85 * board_size) and int(0.2162 * board_size) < y_coord < int(0.3162 * board_size):
                                play_against_a_computer_button_is_selected = True
                            elif int(2.225 * board_size) < x_coord < int(2.85 * board_size) and int(0.5324 * board_size) < y_coord < int(0.6324 * board_size):
                                play_against_a_human_button_is_selected = True
                            elif int(2.225 * board_size) < x_coord < int(2.85 * board_size) and int(0.8486 * board_size) < y_coord < int(0.9486 * board_size):
                                play_a_game_scenario_is_selected = True
                            elif int(2.225 * board_size) < x_coord < int(2.85 * board_size) and int(1.1648 * board_size) < y_coord < int(1.2648 * board_size):
                                see_the_game_history_button_is_selected = True
                            elif int(0.125 * board_size) < x_coord < int(0.225 * board_size) and int(1.256 * board_size) < y_coord < int(1.356 * board_size):
                                minus_button_is_selected = True
                            elif int(0.275 * board_size) < x_coord < int(0.375 * board_size) and int(1.256 * board_size) < y_coord < int(1.356 * board_size):
                                plus_button_is_selected = True

                        if state in ['waiting for 1st click', 'human player moved']:
                            if int(0.125 * board_size) < x_coord < int(0.375 * board_size) and int(0.0655 * board_size) < y_coord < int(0.1655 * board_size):
                                forfeit_button_is_selected = True
                            elif int(0.5 * board_size) < x_coord < int(0.75 * board_size) and int(0.0655 * board_size) < y_coord < int(0.1655 * board_size):
                                exit_button_is_selected = True
                            elif int(2.25 * board_size) < x_coord < int(2.5 * board_size) and int(0.0655 * board_size) < y_coord < int(0.1655 * board_size):
                                flip_the_board_button_is_selected = True
                            elif int(2.625 * board_size) < x_coord < int(2.875 * board_size) and int(0.0655 * board_size) < y_coord < int(0.1655 * board_size):
                                undo_a_move_button_is_selected = True

                            elif int(0.15625 * board_size) < x_coord < int(0.78125 * board_size) and int(how_are_the_points_calculated_button_y_coords * board_size) < y_coord < int((how_are_the_points_calculated_button_y_coords + 0.1) * board_size):
                                how_are_the_points_calculated_button_is_selected = True
                                how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                
                            if int(0.15625 * board_size) < x_coord < int(0.78125 * board_size) and int(show_the_move_history_button_y_coords * board_size) < y_coord < int((show_the_move_history_button_y_coords + 0.1) * board_size):
                                show_the_move_history_button_is_selected = True
                                how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)

                        if state == 'waiting for 1st click':

                            # Feedback
                            # Only expand feedback if there is no cheat limit or a current player hasn't reached the cheat limit yet
                            if cheat_limit == None or (current_color == True and (cheat_counter_white < cheat_limit)) or (current_color == False and (cheat_counter_black < cheat_limit)):

                                # Feedback: Why did {name} make this move?
                                if not move_history == []:
                                    if not selected_feedback_options[0] == True:
                                        if int(2.21875 * board_size) < x_coord < int(2.84375 * board_size) and int(0.395 * board_size) < y_coord < int(0.495 * board_size):
                                            selected_feedback_options[0] = True
                                            if current_color == True:
                                                cheat_counter_white += 1
                                            else: # current_color == False:
                                                cheat_counter_black += 1

                                            # 'Please wait' message
                                            feedbacks[0] = ['Chessonator is thinking, please wait']
                                            what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)
                                            pygame.display.update()

                                            feedback_start_time = time.time()
                                            feedbacks[0] = create_feedback(0, board, current_color, castling_info, move_history, player, initial_castling_info)
                                            feedback_end_time = time.time()
                                            feedback_processing_time = feedback_end_time - feedback_start_time
                                            start_time_human_player += feedback_processing_time


                                            how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                                            what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                                # Feedback: What move should I make?
                                if True:
                                    if not selected_feedback_options[1] == True:
                                        if int(2.21875 * board_size) < x_coord < int(2.84375 * board_size) and int((what_move_should_i_make_y_pos) * board_size) < y_coord < int((what_move_should_i_make_y_pos + 0.1) * board_size):
                                            selected_feedback_options[1] = True
                                            if current_color == True:
                                                cheat_counter_white += 1
                                            else: # current_color == False:
                                                cheat_counter_black += 1

                                            # 'Please wait' message
                                            feedbacks[1] = ['Chessonator is thinking, please wait']
                                            what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)
                                            pygame.display.update()

                                            feedback_start_time = time.time()
                                            feedbacks[1] = create_feedback(1, board, current_color, castling_info, move_history, player, initial_castling_info)
                                            feedback_end_time = time.time()
                                            feedback_processing_time = feedback_end_time - feedback_start_time
                                            start_time_human_player += feedback_processing_time

                                            how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                                            what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                        if state == 'human player moved':

                            # Button: pass the move over to the opponent
                            if int(2.21875 * board_size) < x_coord < int(2.84375 * board_size) and int(1.22475 * board_size) < y_coord < int(1.32475 * board_size):
                                pass_the_move_over_to_the_opponent_button_is_selected = True
                            
                            # Feedback
                            # Only expand feedback if there is no cheat limit or a current player hasn't reached the cheat limit yet
                            if cheat_limit == None or (current_color == True and (cheat_counter_white < cheat_limit)) or (current_color == False and (cheat_counter_black < cheat_limit)):

                                # Feedback: Was that a strong move?
                                if not selected_feedback_options[2] == True:
                                    if int(2.21875 * board_size) < x_coord < int(2.84375 * board_size) and int(0.395 * board_size) < y_coord < int(0.495 * board_size):
                                        selected_feedback_options[2] = True
                                        if current_color == True:
                                            cheat_counter_white += 1
                                        else: # current_color == False:
                                            cheat_counter_black += 1

                                        # 'Please wait' message
                                        feedbacks[2] = ['Chessonator is thinking, please wait']
                                        feedbacks[3] = []
                                        what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)
                                        pygame.display.update()

                                        feedback_start_time = time.time()
                                        feedbacks[2] = create_feedback(2, board, current_color, castling_info, move_history, player, initial_castling_info)
                                        feedback_end_time = time.time()
                                        feedback_processing_time = feedback_end_time - feedback_start_time
                                        start_time_human_player += feedback_processing_time

                                        what_other_move_could_i_make_first_appearance = True

                                # Feedback: What other move could I make?
                                if selected_feedback_options[2] == True:
                                    if not selected_feedback_options[3] == True:
                                        if what_other_move_could_i_make_first_appearance == False:
                                            if int(2.21875 * board_size) < x_coord < int(2.84375 * board_size) and int((what_other_move_could_i_make_y_pos) * board_size) < y_coord < int((what_other_move_could_i_make_y_pos + 0.1) * board_size):
                                                selected_feedback_options[3] = True
                                                if current_color == True:
                                                    cheat_counter_white += 1
                                                else: # current_color == False:
                                                    cheat_counter_black += 1

                                                # 'Please wait' message
                                                feedbacks[3] = ['Chessonator is thinking, please wait']
                                                what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)
                                                pygame.display.update()

                                                feedback_start_time = time.time()
                                                feedbacks[3] = create_feedback(3, board, current_color, castling_info, move_history, player, initial_castling_info)
                                                feedback_end_time = time.time()
                                                feedback_processing_time = feedback_end_time - feedback_start_time
                                                start_time_human_player += feedback_processing_time

                        if state == 'creating a scenario, waiting for 1st click':
                            if int(2.225 * board_size) < x_coord < int(2.85 * board_size) and int(1.07475 * board_size) < y_coord < int(1.17475 * board_size):
                                play_against_a_computer_button_is_selected = True
                            elif int(2.225 * board_size) < x_coord < int(2.85 * board_size) and int(1.22475 * board_size) < y_coord < int(1.32475 * board_size):
                                play_against_a_human_button_is_selected = True
                            elif int(0.15 * board_size) < x_coord < int(0.775 * board_size) and int(1.22475 * board_size) < y_coord < int(1.32475 * board_size):
                                go_back_button_is_selected = True

                # Board interaction
                elif state in ['waiting for 1st click', 'waiting for 2nd click', 'creating a scenario, waiting for 1st click', 'creating a scenario, waiting for 2nd click']: # only if clicked within the chess board
                    position = get_position_from_mouse_click(mouse_coords, board_size, cell_size, upside_down)
                    if state in ['waiting for 1st click', 'creating a scenario, waiting for 1st click']:
                        current_position, state = validate_selected_cell(board, position, current_color, state)
                        if not current_position == None:
                            if state == 'waiting for 2nd click':
                                legal_move_list = create_general_legal_move_list(board, current_position, current_color, castling_info)
                                forfeit_button_is_selected = False
                                exit_button_is_selected = False
                                flip_the_board_button_is_selected = False
                                undo_a_move_button_is_selected = False
                            else: # state == 'creating a scenario, waiting for 2nd click'
                                legal_move_list = generate_legal_move_list_for_creating_a_scenario(board, current_position)

                    elif state in ['waiting for 2nd click', 'creating a scenario, waiting for 2nd click']:
                        new_position = position

                        if state == 'waiting for 2nd click':
                            if current_position == 60 and new_position == 58: # White queenside (left) castling
                                new_position = 103
                            elif current_position == 60 and new_position == 62: # White kingside (right) castling
                                new_position = 104
                            elif current_position == 4 and new_position == 2: # Black queenside (left) castling
                                new_position = 101
                            elif current_position == 4 and new_position == 6: # Black kingside (right) castling
                                new_position = 102

                        if new_position in legal_move_list:

                            if state == 'waiting for 2nd click':
                                make_move(board, current_position, new_position, castling_info, move_history, False)
                                state = 'transition to human player moved'
                                
                            else: # state == 'creating a scenario, waiting for 2nd click'
                                deleted_piece = make_move_when_creating_a_scenario(board, current_position, new_position)
                                if new_position == 74: # needed for animation of trash can
                                    refresh_print_create_game_scenario_elements(board_size, current_position, deleted_piece, legal_move_list, go_back_button_is_selected, play_against_a_computer_button_is_selected, play_against_a_human_button_is_selected)
                                    pygame.display.update()
                                    clock.tick(60)
                                    time.sleep(0.12)
                                state = 'creating a scenario, waiting for 1st click'

                        else:
                            if state == 'waiting for 2nd click':
                                state = 'waiting for 1st click'
                                forfeit_button_is_selected = False
                                exit_button_is_selected = False
                                flip_the_board_button_is_selected = False
                                undo_a_move_button_is_selected = False
                            else: # state == 'creating a scenario, waiting for 2nd click'
                                state = 'creating a scenario, waiting for 1st click'

                        current_position = None
                        legal_move_list = []

            # No click - Button release
            else: # Mouse is released, selected buttons are triggered and no longer selected
                if state == 'welcoming window':
                    if play_against_a_computer_button_is_selected:
                        play_against_a_computer_button_is_selected = False
                        state = 'setup window human vs computer'

                    elif play_against_a_human_button_is_selected:
                        play_against_a_human_button_is_selected = False
                        state = 'setup window human vs human'

                    elif play_a_game_scenario_is_selected:
                        play_a_game_scenario_is_selected = False
                        state = 'select a game scenario'

                    elif see_the_game_history_button_is_selected:
                        see_the_game_history_button_is_selected = False
                        game_history_window(board_size)
                        state = 'transition to the welcoming window'

                    elif minus_button_is_selected:
                        minus_button_is_selected = False
                        if board_size - 80 >= 80:
                            alter_board_size(board_size, difference = -80)
                            # Restarts the program
                            os.execv(sys.executable, ['python'] + sys.argv)

                    elif plus_button_is_selected:
                        plus_button_is_selected = False
                        if board_size + 80 <= 800:
                            alter_board_size(board_size, difference = 80)
                            # Restarts the program
                            os.execv(sys.executable, ['python'] + sys.argv)

                if state in ['waiting for 1st click', 'waiting for 2nd click', 'human player moved']:
                    if forfeit_button_is_selected:
                        forfeit_button_is_selected = False

                        if len(move_history) > 2:
                            show_undo_button = True
                        else:
                            show_undo_button = False

                        undo_a_move_button_is_selected = game_over_window(4, player, move_counter, average_time_per_move_white, average_time_per_move_black, show_undo_button, how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords)
                    
                        if undo_a_move_button_is_selected:

                            undo_a_move(board, move_history)
                            undo_a_move(board, move_history)

                            if not move_history == []:
                                castling_info = move_history[-1][-1][:]
                            else:
                                castling_info = castling_info = initial_castling_info[:]

                            move_counter -= 1
                                       
                            #current_color = not current_color
                            current_position = None # so that there would be no highlighted cells on the board
                            legal_move_list = []

                            how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                            what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                        else:
                            state = 'transition to the welcoming window'

                    elif exit_button_is_selected:
                        exit_button_is_selected = False

                        cancel = exit_warning_window(board_size, how_are_the_points_calculated_button_y_coords)

                        if not cancel:
                            state = 'transition to the welcoming window'

                        how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                        what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                    elif flip_the_board_button_is_selected:
                        flip_the_board_button_is_selected = False
                        upside_down = not upside_down # flips the board
                        pass

                    elif undo_a_move_button_is_selected:
                        undo_a_move_button_is_selected = False

                        # Only undo if there is no cheat limit or a current player hasn't reached the cheat limit yet
                        if cheat_limit == None or (current_color == True and (cheat_counter_white < cheat_limit)) or (current_color == False and (cheat_counter_black < cheat_limit)):

                            selected_feedback_options = [False, False, False, False, False, False] # Collapse all feedback windows

                            if (not state == 'human player moved'): # If a player hasn't made a move yet, undo twice
                                if not move_counter == 1:
                                    undo_a_move(board, move_history)
                                    undo_a_move(board, move_history)

                                    if not move_history == []:
                                        castling_info = move_history[-1][-1][:]
                                    else:
                                        castling_info = initial_castling_info[:]

                                    move_counter -= 1

                                    if current_color == True:
                                        cheat_counter_white += 1
                                    else: # current_color == False:
                                        cheat_counter_black += 1

                                    state = 'waiting for 1st click'
                            else:
                                undo_a_move(board, move_history)

                                if not move_history == []:
                                    castling_info = move_history[-1][-1][:]
                                else:
                                    castling_info = initial_castling_info[:]

                                if current_color == True:
                                    cheat_counter_white += 1
                                else: # current_color == False:
                                    cheat_counter_black += 1

                                state = 'waiting for 1st click'

                            current_position = None # so that there would be no highlighted cells on the board
                            legal_move_list = []

                            how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                            what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                    elif how_are_the_points_calculated_button_is_selected:
                        how_are_the_points_calculated_button_is_selected = False
                        how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                        
                        how_are_the_points_calculated_window(board_size, how_are_the_points_calculated_button_y_coords)

                        how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                        what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                    elif show_the_move_history_button_is_selected:
                        show_the_move_history_button_is_selected = False
                        how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)

                        move_history_window(board_size, state, player, current_color, move_history)

                        how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                        what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)

                if state == 'human player moved':
                    if pass_the_move_over_to_the_opponent_button_is_selected:
                        pass_the_move_over_to_the_opponent_button_is_selected = False

                        end_time_human_player = time.time() # Stops the stopwatch - human has completed a move

                        if current_color == True: # White
                            white_move_times.append(round(end_time_human_player - start_time_human_player, 1))
                            average_time_per_move_white = calculate_average_time_per_move(white_move_times)
                        else: # current_player == False: # Black
                            black_move_times.append(round(end_time_human_player - start_time_human_player, 1))
                            average_time_per_move_black = calculate_average_time_per_move(black_move_times)

                        what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)
                        state = 'next player'
                
                if state == 'creating a scenario, waiting for 1st click':
                    if play_against_a_computer_button_is_selected:
                        play_against_a_computer_button_is_selected = False
                        
                        go_back, _, _, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black = setup_human_vs_computer(board_size)

                        if not go_back:
                            initial_castling_info = approximate_castling_info(board)
                            scenario_name = scenario_name_input_window(board_size)
                            add_a_game_scenario(scenario_name, board, initial_castling_info, current_color, player)
                            state = 'new game'

                    elif play_against_a_human_button_is_selected:
                        play_against_a_human_button_is_selected = False

                        go_back, _, _, player, current_color, time_limit, cheat_limit, cheat_counter_white, cheat_counter_black = setup_human_vs_human(board_size)

                        if not go_back:
                            initial_castling_info = approximate_castling_info(board)
                            scenario_name = scenario_name_input_window(board_size)
                            add_a_game_scenario(scenario_name, board, initial_castling_info, current_color, player)
                            state = 'new game'

                    elif go_back_button_is_selected:
                        go_back_button_is_selected = False
                        state = 'select a game scenario'

        # GUI refresh
        if True:
            refresh_print_board_GUI(board, board_size, cell_size, current_position, computer_current_position, computer_new_position, legal_move_list, upside_down)
            
            if state == 'welcoming window':
                refresh_print_welcoming_window(board_size, play_against_a_computer_button_is_selected, play_against_a_human_button_is_selected, play_a_game_scenario_is_selected, see_the_game_history_button_is_selected, minus_button_is_selected, plus_button_is_selected)
            if state == 'turn passed to a computer':
                refresh_print_computer_is_thinking(board_size)
            if state in ['transition to human player moved', 'human player moved', 'next player', 'turn passed to a computer', 'computer player moved']:
                if current_color == False and state == 'next player': # Increment the move_counter only if the move is passed over to the white player.
                    move_counter += 1 # move_counter is only used for game_statistics
                how_are_the_points_calculated_button_y_coords, show_the_move_history_button_y_coords = refresh_print_game_statistics(move_counter, state, board_size, player, current_color, move_history, cheat_limit, cheat_counter_white, cheat_counter_black, average_time_per_move_white, average_time_per_move_black, how_are_the_points_calculated_button_is_selected, show_the_move_history_button_is_selected, board)
                what_move_should_i_make_y_pos, what_other_move_could_i_make_y_pos, what_other_move_could_i_make_first_appearance = refresh_print_feedback(state, feedbacks, board_size, player, current_color, move_history, selected_feedback_options, pass_the_move_over_to_the_opponent_button_is_selected, what_other_move_could_i_make_first_appearance)
            if state in ['waiting for 1st click', 'waiting for 2nd click', 'human player moved']:
                refresh_print_remaining_time(board_size, state, start_time_human_player, time_limit)
                refresh_print_gameplay_buttons(board_size, forfeit_button_is_selected, exit_button_is_selected, flip_the_board_button_is_selected, undo_a_move_button_is_selected)
            if state in ['creating a scenario, waiting for 1st click', 'creating a scenario, waiting for 2nd click']:
                deleted_piece = None
                refresh_print_create_game_scenario_elements(board_size, current_position, deleted_piece, legal_move_list, go_back_button_is_selected, play_against_a_computer_button_is_selected, play_against_a_human_button_is_selected)

        # Keeps the frames running
        # I don't really know how
        pygame.display.update()
        clock.tick(60)