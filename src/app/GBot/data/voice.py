from enum import Enum, auto
from typing import Dict, Union


class VoiceState(Enum):
    NOT_PLAYED = auto()
    YOMIAGE = auto()
    MUSIC = auto()
    VC_RECORD = auto()


class VoiceManager:
    """VoiceClientの使用状況を管理するクラス

    """
    voice: Dict[int, "VoiceManager"] = {}

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.state: VoiceState = VoiceState.NOT_PLAYED

    def get(self) -> Union[None, "VoiceManager"]:
        """_summary_

        Returns:
            Union[None, "VoiceManager"]: self.voiceに該当するVoiceManagerを返す。なければNoneを返す。
        """
        if self.guild_id in self.voice:
            return self.voice[self.guild_id]
        else:
            return None

    def set(self, state: VoiceState):
        """_summary_

        Args:
            state (VoiceState): VoiceStateを指定する。
        """
        self.state = state

    def remove(self):
        """self.voiceから該当するVoiceManagerを削除する。
        """
        self.voice.pop(self.guild_id)

    @classmethod
    def create(cls, guild_id: int) -> "VoiceManager":
        """VoiceManagerを作成する。

        Args:
            guild_id (int): GuildのIDを指定する。

        Returns:
            VoiceManager: VoiceManagerを返す。
        """
        cls.voice[guild_id] = cls(guild_id)
        return cls.voice[guild_id]
