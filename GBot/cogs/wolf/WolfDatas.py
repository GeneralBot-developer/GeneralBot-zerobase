from enum import Enum


class Role_List(Enum):
    VILLAGER = 0
    FORTUNE_TELLER = 1
    HUNTER = 2
    WEREWOLF = 3
    MEDIUM = 4
    MADMAN = 5


class Day_Cycles(Enum):
    DAY = 0
    EVENING = 1
    NIGHT = 2


class FortuneTeller:
    name = "占い師"
    role = Role_List.FORTUNE_TELLER


class Hunter:
    name = "狩人"
    role = Role_List.HUNTER


class Werewolf:
    name = "人狼"
    role = Role_List.WEREWOLF


class Medium:
    name = "占い師"
    role = Role_List.MEDIUM


class Madman:
    name = "狂人"
    role = Role_List.MADMAN


class Villager:
    name = "村人"
    role = Role_List.VILLAGER
