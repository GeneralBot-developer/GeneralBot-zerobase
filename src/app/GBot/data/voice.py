from enum import Enum, auto
from typing import Dict, Set, Union


class VoiceState(Enum):
    NOT_PLAYED = auto()
    YOMIAGE = auto()
    MUSIC = auto()
    VC_RECORD = auto()


class VoiceManager:
    voice: Dict[int, "VoiceManager"] = {}

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.state: VoiceState = VoiceState.NOT_PLAYED

    # 存在しなければ新しくVoiceManagerを作成してvoiceに登録して返す
    def get(self) -> Union[None, "VoiceManager"]:
        if self.guild_id in self.voice:
            return self.voice[self.guild_id]
        else:
            return None

    def set(self, state: VoiceState):
        self.state = state

    def remove(self):
        self.voice.pop(self.guild_id)

    @classmethod
    def create(cls, guild_id: int):
        cls.voice[guild_id] = cls(guild_id)
        return cls.voice[guild_id]
