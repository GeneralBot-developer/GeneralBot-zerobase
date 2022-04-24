from discord.opus import Decoder as DiscordDecoder
from discord.opus import exported_functions, OpusError, c_float_ptr
import sys
import ctypes
import os
import logging
import struct
from typing import Union

log = logging.getLogger(__name__)


_lib = None


def libopus_loader(name: str) -> ctypes.CDLL:
    """渡されたライブラリ名を持つCDLLオブジェクトを返す。

    Args:
        name (str): 読み込みたいライブラリ名

    Returns:
        ctypes.CDLL: 読み込まれたcdllライブラリの実体
    """
    # create the library...
    lib = ctypes.cdll.LoadLibrary(name)

    # register the functions...
    for item in exported_functions:
        func = getattr(lib, item[0])

        try:
            if item[1]:
                func.argtypes = item[1]

            func.restype = item[2]
        except KeyError:
            pass

        try:
            if item[3]:
                func.errcheck = item[3]
        except KeyError:
            log.exception("Error assigning check function to %s", func)

    return lib


def _load_default() -> Union[ctypes.CDLL, None]:
    """libopusをロードしてCDLLオブジェクトを返す。

    Returns:
        Union[ctypes.CDLL, None]: libopusを読み込む。もしも読み込みに失敗したらNoneを返す。
    """
    global _lib
    try:
        if sys.platform == 'win32':
            _basedir = os.path.dirname(os.path.abspath(__file__))
            _bitness = struct.calcsize('P') * 8
            _target = 'x64' if _bitness > 32 else 'x86'
            _filename = os.path.join(
                _basedir,
                'bin', 'libopus-0.{}.dll'.format(
                    _target
                )
            )
            _lib = libopus_loader(_filename)
        else:
            _lib = libopus_loader(ctypes.util.find_library('opus'))
    except Exception:
        _lib = None

    return _lib is not None


def is_loaded() -> bool:
    """libopusがロードされているかどうかを返す。

    Returns:
        bool: libopusがロードされているかどうか
    """
    global _lib
    return _lib is not None


class Decoder(DiscordDecoder):
    @staticmethod
    def packet_get_nb_channels(data: bytes) -> int:
        return 2

    def decode_float(self, data: bytes, *, fec: bool=False) -> float:
        """ dataでopusのデコードしてfloat型のデータを返す。

        Args:
            data (_type_): opusのデコードデータ
            fec (bool, optional): fecを使うかどうか。デフォルトはFalse。

        Raises:
            OpusError: opusのエラーが発生した場合に発生

        Returns:
            float: opusのデコードデータ
        """
        if not is_loaded():
            _load_default()
        if data is None and fec:
            raise OpusError(
                "Invalid arguments: FEC cannot be used with null data"
            )

        if data is None:
            frame_size = self._get_last_packet_duration(
            ) or self.SAMPLES_PER_FRAME
            channel_count = self.CHANNELS
        else:
            frames = self.packet_get_nb_frames(data)
            channel_count = self.packet_get_nb_channels(data)
            samples_per_frame = self.packet_get_samples_per_frame(data)
            frame_size = frames * samples_per_frame

        pcm = (ctypes.c_float * (frame_size * channel_count))()
        pcm_ptr = ctypes.cast(pcm, c_float_ptr)

        ret = _lib.opus_decode_float(
            self._state,
            data,
            len(data) if data else 0, pcm_ptr, frame_size, fec)

        return pcm[:ret * channel_count]
