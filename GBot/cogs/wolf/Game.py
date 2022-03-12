import random
from typing import List, Dict
from .WolfDatas import Role_List, Day_Cycles, FortuneTeller, Hunter, Werewolf, Medium, Madman, Villager

# 人狼ゲームのセッション本体, このクラスはゲームを実行するためのクラスです


class WolfGame:
    def __init__(self, guild_id: int, author_id: int, channel: int):
        self.guild_id = guild_id
        self.entry_list = []
        self.player_list: Dict[int, Role_List] = {}
        self.channel: int
        self.day_cycle: Day_Cycles = Day_Cycles.DAY
        self.votelist: List[int] = []
        self.author_id: int

    @classmethod
    def session_create(
            cls,
            guild_id: int,
            user_id,
            channel: int
    ) -> "WolfGame":
        return WolfGame(guild_id=guild_id, author_id=user_id, channel=channel)

    def join(self, user_id: int):
        self.entry_list.append(user_id)

    def leave(self, user_id: int):
        self.entry_list.remove(user_id)

    def close(self):
        self.entry_list.clear()

    def start(self):
        self.player_list.clear()
        wolfs = random.sample(self.entry_list, len(self.entry_list) // 4)
        for user_id in self.entry_list:
            if user_id in wolfs:
                wolf_role = random.choice([Madman, Werewolf])
                self.player_list[user_id] = wolf_role.role
            else:
                role = random.choice([FortuneTeller, Hunter, Medium, Villager])
                self.player_list[user_id] = role.role

    def turn_start(self):
        self.day_cycle = Day_Cycles.DAY

    def turn_end(self):
        self.day_cycle = Day_Cycles.EVENING

    def post_end(self):
        self.day_cycle = Day_Cycles.NIGHT

    def end(self):
        self.player_list.clear()
        self.entry_list.clear()

    def get_player_list(self) -> List[int]:
        return self.entry_list

    def get_player_role(self, user_id: int) -> Role_List:
        return self.player_list[user_id]

    def vote(self, target_id: int):
        self.votelist.append(target_id)

    def return_vote(self) -> List[int]:
        return self.votelist

# 人狼ゲームのセッション管理クラス, このクラスはゲームを管理するためのクラスです


class SessionManager:
    game_list: List[WolfGame] = []

    def __init__(self, guild_id: int):
        self.guild_id = guild_id

    @classmethod
    def game_create(cls, guild_id: int) -> WolfGame:
        game = WolfGame.session_create(guild_id)
        cls.game_list.append(game)
        return game

    def get(self) -> bool:
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                return True
        return False

    def join(self, user_id: int):
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                game.join(user_id)

    def get_list(self) -> List[WolfGame]:
        return self.game_list

    def leave(self, user_id: int):
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                game.leave(user_id)

    def close(self):
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                game.session_close()

    def start(self):
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                game.session_start()

    def end(self):
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                game.session_end()

    def get_player_list(self) -> List[int]:
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                return game.session_get_player_list()

    def get_player_role(self, user_id: int) -> Role_List:
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                return game.session_get_player_role(user_id)

    def get_player_role_list(self) -> List[Role_List]:
        role_list = []
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                for user_id in game.session_get_player_list():
                    role_list.append(game.session_get_player_role(user_id))
        return role_list

    def vote(self, target_id: int):
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                game.vote(target_id)

    # 全プレイヤーが投票したかどうか
    def is_vote_all(self) -> bool:
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                if len(game.return_vote()) == len(game.session_get_player_list()):
                    return True
        return False

    # votelistの最頻値を求める
    def vote_result(self) -> int:
        votelist = []
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                votelist = game.return_vote()
        return max(set(votelist), key=votelist.count)

    def get_player_role_count(self) -> Dict[Role_List, int]:
        role_count = {}
        for role in Role_List:
            role_count[role] = 0
        for game in self.game_list:
            if game.guild_id == self.guild_id:
                for user_id in game.session_get_player_list():
                    role_count[game.session_get_player_role(user_id)] += 1
        return role_count


