import random


class WolfGame:
    def __init__(self, guild_id):
        self.entry_users = []
        self.guild_id = guild_id
        self.alive_users = []
        self.wolf_id = []
        self.playing_channel: int

    def game_join(self, user_id, channel_id):
        self.playing_channel = channel_id
        self.entry_users.append(user_id)

    def game_leave(self, user_id):
        self.playing_channel = None
        self.entry_users.remove(user_id)

    # 参加人数によって人狼の数を変動させる
    def game_start(self):
        if len(self.entry_users) < 5:
            return "エントリー人数が足りません"
        if len(self.entry_users) <= 5:
            self.wolf_id = random.sample(self.entry_users, 1)
        else:
            self.wolf_id = random.sample(self.entry_users, 2)
        self.alive_users = self.entry_users.copy()
        self.entry_users.clear()

    async def game_execution_vote(self):
        pass
