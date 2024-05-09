from __future__ import annotations

from typing import Union
from functools import lru_cache
import random
import abc
import enum

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

    def take_turn(self):
        pass
        