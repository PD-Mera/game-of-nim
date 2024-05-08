from __future__ import annotations

from typing import Union

import abc
import enum

from exceptions import TupleLengthMismatch, InvalidPile, InvalidNumber

def tuple_element_wise_minus(tuple1: tuple, tuple2: tuple):
    if len(tuple1) != len(tuple2): raise TupleLengthMismatch(f"Length of tuple 1 ({len(tuple1)}) must match tuple 2 ({len(tuple2)})")
    return tuple(element1 - element2 for element1, element2 in zip(tuple1, tuple2))

class PlayerType(str, enum.Enum):
    HUMAN = "Human"
    AI = "AI"

class Player:
    def __init__(self, player_type: PlayerType, is_first_player: bool) -> None:
        self.player_type = player_type
        if is_first_player:
            self.player_order = 1
        else:
            self.player_order = 2

    def __cstr__(self):
        return f"Player {self.player_order} ({self.player_type})"

    def is_human(self):
        return True if self.player_type == PlayerType("Human") else False

    def take_turn(self, state, nim_game: Union[BaseNim, None] = None):
        pass
        
        # if self.is_human():
        #     if isinstance(state, int):
        #         take_number = int(input(f"Player {self.player_order} ({self.player}) take: "))
        #         new_state = state - take_number
        #         print(f"Player {self.player_order} ({self.player}) turn: Take {take_number} | Left {new_state}")
        #     elif isinstance(state, (tuple, list)):
        #         pile = int(input(f"Player {self.player_order} ({self.player}) choose pile: "))
        #         if pile - 1 not in range(len(state)):
        #             raise InvalidPile(f"Pile must be in range (1-{len(state)})")
                
        #         take_number = int(input(f"Player {self.player_order} ({self.player}) take: "))
        #         if state[pile - 1] - take_number < 0:
        #             raise InvalidNumber(f"Number must be in range (1-{state[pile - 1]})")
        #         elif take_number < 1:
        #             raise InvalidNumber(f"Number must be > 0")
                
        #         take_tuple = [0] * len(state)
        #         take_tuple[pile - 1] = take_number
        #         take_tuple = tuple(take_tuple)
        #         new_state = state[:pile - 1] + (state[pile - 1] - take_number,) + state[pile :]
        #         print(f"Player {self.player_order} ({self.player}) turn: Take {take_tuple} | Left {new_state}")
        #     else:
        #         raise NotImplementedError

        # else:
        #     assert nim_game is not None
        #     score, new_state = nim_game.best_move(state)
        #     print(f"Player {self.player_order} ({self.player}) turn: Take {tuple_element_wise_minus(state, new_state)} | Left {new_state}")

        # return new_state

class BaseNim(metaclass=abc.ABCMeta):
    def minimax(self, state, is_maximizing):
        if (score := self.evaluate(state, is_maximizing)) is not None:
            return score
        
        return (max if is_maximizing else min)(
            self.minimax(new_state, is_maximizing=not is_maximizing)
            for new_state in self.possible_new_states(state)
        )
    
    def best_move(self, state):
        return max(
            (self.minimax(new_state, is_maximizing=False), new_state)
            for new_state in self.possible_new_states(state)
        )

    @abc.abstractmethod
    def possible_new_states(self, state):
        """Return possible new states from one state"""

    @abc.abstractmethod
    def evaluate(self, state, is_maximizing):
        """Evaluate the state is max or min"""

    @abc.abstractmethod
    def computer_turn(self, state, player: Player):
        """AI play"""

    @abc.abstractmethod
    def human_turn(self, state, player: Player):
        """Human play"""

    @abc.abstractmethod
    def game_loop(self, starting_state, player1: Player, player2: Player):
        
        """Loop through the game"""

class SimpleNim(BaseNim):
    def possible_new_states(self, state: int):
        return [state - take for take in (1, 2, 3) if take <= state]
    
    def evaluate(self, state: int, is_maximizing: bool):
        if state == 0:
            return 1 if is_maximizing else -1
        
    def computer_turn(self, state: int, player: Player):
        score, new_state = self.best_move(state)
        print(player.__cstr__(), f"turn: Take {state - new_state} | Left {new_state}")
        return new_state
    
    def human_turn(self, state: int, player: Player):
        take_number = int(input(player.__cstr__() + f"take: "))
        if take_number not in (1, 2, 3):
            raise InvalidNumber(f"Number must be in range (1-3)")

        new_state = state - take_number
        print(player.__cstr__(), f"turn: Take {take_number} | Left {new_state}")
        return new_state
    
    def game_loop(self, starting_state: int, player1: Player, player2: Player):
        player1.take_turn = self.human_turn if player1.is_human() else self.computer_turn
        player2.take_turn = self.human_turn if player2.is_human() else self.computer_turn

        assert player1.player_order != player2.player_order
        state = starting_state

        print(f"Starting Pile: {state}")
        while True:
            try:
                state1 = player1.take_turn(state, player1)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if sum(state1) == 1:
                print(player1.__cstr__(), "wins! Game ends.")
                break

            try:
                state2 = player2.take_turn(state1, player2)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if sum(state1) == 1:
                print(player2.__cstr__(), "wins! Game ends.")
                break
            state = state2
        
class RegularNim(BaseNim):
    def possible_new_states(self, state: tuple[int]):
        for pile, counters in enumerate(state):
            for remain in range(counters):
                yield state[:pile] + (remain,) + state[pile + 1 :]

    def evaluate(self, state: tuple[int], is_maximizing):
        if all(counters == 0 for counters in state):
            return 1 if is_maximizing else -1
        
    def computer_turn(self, state: tuple[int], player: Player):
        score, new_state = self.best_move(state)
        print(player.__cstr__(), f"turn: Take {tuple_element_wise_minus(state, new_state)} | Left {new_state}")
        return new_state
    
    def human_turn(self, state: tuple[int], player: Player):
        take_number = int(input(player.__cstr__() + f"take: "))
        if take_number not in (1, 2, 3):
            raise InvalidNumber(f"Number must be in range (1-3)")

        new_state = state - take_number
        print(player.__cstr__(), f"turn: Take {take_number} | Left {new_state}")
        return new_state
    
    def game_loop(self, starting_state: tuple[int], player1: Player, player2: Player):
        player1.take_turn = self.human_turn if player1.is_human() else self.computer_turn
        player2.take_turn = self.human_turn if player2.is_human() else self.computer_turn

        assert player1.player_order != player2.player_order
        state = starting_state
        print(f"Starting Pile: {state}")
        while True:
            try:
                state1 = player1.take_turn(state, player1)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if sum(state1) == 1:
                print(player1.__cstr__(), "wins! Game ends.")
                break

            try:
                state2 = player2.take_turn(state1, player2)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if sum(state2) == 1:
                print(player2.__cstr__(), "wins! Game ends.")
                break
            state = state2
    
class MisereNim(RegularNim):
    def evaluate(self, state: tuple[int], is_maximizing):
        if all(counters == 0 for counters in state):
            return -1 if is_maximizing else 1

    def game_loop(self, starting_state: tuple[int], player1: Player, player2: Player):
        player1.take_turn = self.human_turn if player1.is_human() else self.computer_turn
        player2.take_turn = self.human_turn if player2.is_human() else self.computer_turn

        assert player1.player_order != player2.player_order
        state = starting_state
        print(f"Starting Pile: {state}")
        while True:
            try:
                state1 = player1.take_turn(state, player1)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if sum(state1) == 0:
                print(player1.__cstr__(), "wins! Game ends.")
                break

            try:
                state2 = player2.take_turn(state1, player2)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if sum(state2) == 0:
                print(player2.__cstr__(), "wins! Game ends.")
                break
            state = state2

class SplitNim(BaseNim):
    @staticmethod
    def split_pile(pile: int):
        for i in range(pile // 2 + 1, pile):
            if i == pile - i:
                continue

            yield (i, pile - i)
            
    def split_piles(self, piles: tuple[int]):
        for idx_pile, pile in enumerate(piles):
            other_piles = piles[:idx_pile] + piles[idx_pile + 1:]

            possible_split_piles = tuple(self.split_pile(pile))
            for possible_split_pile in possible_split_piles:
                new_possible_pile = (possible_split_pile + other_piles)
                yield new_possible_pile

    
    def possible_new_states(self, state: tuple[int]):
        return list(self.split_piles(state))
        # new_state = []
        # for pile in state:
        #     posible_state = []


        # for pile, counters in enumerate(state):
        #     for remain in range(counters):
        #         yield state[:pile] + (remain,) + state[pile + 1 :]

    def evaluate(self, state, is_maximizing):
        if all(counters in [1, 2] for counters in state):
            return 1 if is_maximizing else -1
        
    def game_loop(self, starting_state, player1: Player, player2: Player):
        assert player1.player_order != player2.player_order
        state = starting_state
        print(f"Starting Pile: {state}")
        while True:
            try:
                state1 = player1.take_turn(state, self)
            except Exception as e:
                print(f"[{e.__class__.__name__}]: {e}!!! Replay")
                continue

            if sum(state1) == 0:
                print(f"Player {player2.player_order} ({player2.player}) loses! Game ends.")
                break

            try:
                state2 = player2.take_turn(state1, self)
            except Exception as e:
                print(f"[{e.__class__.__name__}]: {e}!!! Replay")
                continue

            if sum(state2) == 0:
                print(f"Player {player1.player_order} ({player1.player}) loses! Game ends.")
                break
            state = state2

if __name__ == "__main__":
    nim_game = MisereNim()
    player1 = Player("AI", is_first_player=True)
    player2 = Player("AI", is_first_player=False)
    nim_game.game_loop(starting_state=(5, 6, 2), player1=player1, player2=player2)
