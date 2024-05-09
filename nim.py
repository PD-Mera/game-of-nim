from __future__ import annotations

from typing import Union
from functools import lru_cache
import random
import abc
import enum

from exceptions import TupleLengthMismatch, InvalidPile, InvalidNumber
from players import Player

def tuple_element_wise_minus(tuple1: tuple, tuple2: tuple):
    if len(tuple1) != len(tuple2): raise TupleLengthMismatch(f"Length of tuple 1 ({len(tuple1)}) must match tuple 2 ({len(tuple2)})")
    return tuple(element1 - element2 for element1, element2 in zip(tuple1, tuple2))

class BaseNim(metaclass=abc.ABCMeta):
    max_piles = 3
    max_numbers = 15
    
    @lru_cache(maxsize=None)
    def minimax(self, state, is_maximizing, alpha=-1, beta=1):
        if (score := self.evaluate(state, is_maximizing)) is not None:
            return score
        
        scores = []
        for new_state in self.possible_new_states(state):
            scores.append(
                score := self.minimax(new_state, not is_maximizing, alpha, beta)
            )
            if is_maximizing:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            if beta <= alpha:
                break
        return (max if is_maximizing else min)(scores)
    
    @lru_cache(maxsize=None)
    def base_minimax(self, state, is_maximizing):
        if (score := self.evaluate(state, is_maximizing)) is not None:
            return score
        
        return (max if is_maximizing else min)(
            self.base_minimax(new_state, is_maximizing=not is_maximizing)
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
    def game_loop(self, player1: Player, player2: Player, starting_state: Union[int, tuple[int], None] = None):
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
    
    def game_loop(self, player1: Player, player2: Player, starting_state: Union[int, tuple[int], None] = None):
        player1.take_turn = self.human_turn if player1.is_human() else self.computer_turn
        player2.take_turn = self.human_turn if player2.is_human() else self.computer_turn
        assert player1.player_order != player2.player_order

        if starting_state is None:
            state = random.randint(5, self.max_numbers)
        elif isinstance(starting_state, tuple):
            state = starting_state[0]
        else:
            state = starting_state

        print(f"Starting Pile: {state}")
        while True:
            try:
                state1 = player1.take_turn(state, player1)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if state1 == 1:
                print(player1.__cstr__(), "wins! Game ends.")
                break

            try:
                state2 = player2.take_turn(state1, player2)
            except Exception as e:
                print(e.__cstr__(), "Replay!!!")
                continue

            if state2 == 1:
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
        pile = int(input(player.__cstr__(), f"choose pile: "))
        if pile - 1 not in range(len(state)):
            raise InvalidPile(f"Pile must be in range (1-{len(state)})")
        
        take_number = int(input(player.__cstr__(), f"take: "))
        if state[pile - 1] - take_number < 0:
            raise InvalidNumber(f"Number must be in range (1-{state[pile - 1]})")
        elif take_number < 1:
            raise InvalidNumber(f"Number must be > 0")
        
        take_tuple = [0] * len(state)
        take_tuple[pile - 1] = take_number
        take_tuple = tuple(take_tuple)
        new_state = state[:pile - 1] + (state[pile - 1] - take_number,) + state[pile :]
        print(player.__cstr__(), f"turn: Take {take_tuple} | Left {new_state}")
        return new_state
    
    def game_loop(self, player1: Player, player2: Player, starting_state: Union[tuple[int], None] = None):
        player1.take_turn = self.human_turn if player1.is_human() else self.computer_turn
        player2.take_turn = self.human_turn if player2.is_human() else self.computer_turn
        assert player1.player_order != player2.player_order

        if starting_state is None:
            state = tuple([random.randint(1, self.max_numbers) for _ in range(random.randint(1, self.max_piles))])
        else:
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

    def game_loop(self, player1: Player, player2: Player, starting_state: Union[tuple[int], None] = None):
        player1.take_turn = self.human_turn if player1.is_human() else self.computer_turn
        player2.take_turn = self.human_turn if player2.is_human() else self.computer_turn
        assert player1.player_order != player2.player_order

        if starting_state is None:
            state = tuple([random.randint(1, self.max_numbers) for _ in range(random.randint(1, self.max_piles))])
        else:
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
    def possible_new_states(self, state: tuple[int]):
        for pile, counters in enumerate(state):
            for take in range(1, (counters + 1) // 2):
                yield state[:pile] + (counters - take, take) + state[pile + 1 :]

    def evaluate(self, state, is_maximizing):
        if all(counters in [1, 2] for counters in state):
            return -1 if is_maximizing else 1
        
    def computer_turn(self, state: tuple[int], player: Player):
        score, new_state = self.best_move(state)
        print(player.__cstr__(), f"turn: Split {state} to {new_state}")
        return new_state
    
    def human_turn(self, state: tuple[int], player: Player):
        pile = int(input(player.__cstr__(), f"choose pile: "))
        if pile - 1 not in range(len(state)):
            raise InvalidPile(f"Pile must be in range (1-{len(state)})")
        
        split_number = int(input(player.__cstr__(), f"split: "))
        if state[pile - 1] - split_number < 0:
            raise InvalidNumber(f"Number must be in range (1-{state[pile - 1]})")
        elif split_number < 1:
            raise InvalidNumber(f"Number must be > 0")
        elif state[pile - 1] == split_number * 2:
            raise InvalidNumber(f"Number must not be half of that pile ({state[pile - 1]} / 2 = {split_number})")
        

        new_state = state[:pile - 1] + (state[pile - 1] - split_number, split_number) + state[pile :]
        print(player.__cstr__(), f"turn: Split {state} to {new_state}")
        return new_state

    def game_loop(self, player1: Player, player2: Player, starting_state: Union[tuple[int], None] = None):
        player1.take_turn = self.human_turn if player1.is_human() else self.computer_turn
        player2.take_turn = self.human_turn if player2.is_human() else self.computer_turn
        assert player1.player_order != player2.player_order

        if starting_state is None:
            state = (random.randint(5, self.max_numbers), )
        else:
            state = starting_state

        print(f"Starting Pile: {state}")
        while True:
            try:
                state1 = player1.take_turn(state, player1)
            except Exception as e:
                print(f"[{e.__class__.__name__}]: {e}!!! Replay")
                continue

            if all(counters in [1, 2] for counters in state1):
                print(player1.__cstr__(), "wins! Game ends.")
                break

            try:
                state2 = player2.take_turn(state1, player2)
            except Exception as e:
                print(f"[{e.__class__.__name__}]: {e}!!! Replay")
                continue

            if all(counters in [1, 2] for counters in state2):
                print(player2.__cstr__(), "wins! Game ends.")
                break
            state = state2
