import random


class WolfGame:
    def __init__(self, guild_id):
        self.entry = []
        self.guild_id = guild_id
        self.users = []
        self.wolf_id = []

    def join(self, user_id: int):
        self.users.append(user_id)

    def leave(self, user_id: int):
        self.entry.remove(user_id)

    def start(self):
        if len(self.users) < 3:
            return "人数が不足しています：人数は3人以上にしてください。"

        self.wolf_id = random.choice(self.users)

        return f"{self.wolf_id} が狼です。"

    def is_wolf(self, user_id: int):
        return self.wolf_id == user_id

    def is_alive(self, user_id: int):
        return user_id in self.users

    def is_dead(self, user_id: int):
        return user_id not in self.users

    def kill(self, user_id: int):
        self.leave(user_id)

    def is_wolf_alive(self):
        return self.wolf_id in self.users

    def is_wolf_dead(self):
        return self.wolf_id not in self.users

    def kill_wolf(self):
        self.leave(self.wolf_id)

    def is_wolf_kill_wolf(self):
        return self.wolf_id == self.wolf_id

