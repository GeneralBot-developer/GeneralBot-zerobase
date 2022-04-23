from discord.gateway import DiscordVoiceWebSocket
from discord import VoiceClient
import struct
import time
import nacl.secret
from collections import defaultdict
from itertools import zip_longest
import numpy as np
from .decoder import Decoder
import wave
from io import BytesIO
import asyncio

MAX_SRC = 65535


class PacketQueue:
    def __init__(self):
        self.queues = defaultdict(list)

    def push(self, packet):
        self.queues[packet.ssrc].append(packet)

    def get_all_ssrc(self):
        return self.queues.keys()

    def get_packets(self, ssrc: int):
        last_seq = None
        packets = self.queues[ssrc]

        while packets:
            if last_seq is None:
                packet = packets.pop(0)
                last_seq = packet.seq
                yield packet
                continue

            if last_seq == MAX_SRC:
                last_seq = -1

            if packets[0].seq - 1 == last_seq:
                packet = packets.pop(0)
                last_seq = packet.seq
                yield packet
                continue

            # 順番がおかしかったときの場合
            for i in range(1, min(1000, len(packets))):
                if packets[i].seq - 1 == last_seq:
                    packet = packets.pop(0)
                    last_seq = packet.seq
                    yield packet
                    break
            else:
                #  該当するパケットがなかった場合、破損していたとみなす
                yield None

        # 終了
        yield -1


class BufferDecoder:
    def __init__(self):
        self.queue = PacketQueue()

    def recv_packet(self, packet):
        self.queue.push(packet)

    async def _decode(self, ssrc):
        decoder = Decoder()
        pcm = []
        start_time = None

        last_timestamp = None

        for packet in self.queue.get_packets(ssrc):
            if packet == -1:
                # 終了
                break
            if packet is None:
                # パケット破損の場合
                data = decoder.decode_float(None)
                pcm += data
                last_timestamp = None
                continue

            if start_time is None:
                start_time = packet.real_time
            else:
                start_time = min(packet.real_time, start_time)

            if len(packet.decrypted) < 10:
                # パケットがdiscordから送られてくる無音のデータだった場合: https://discord.com/developers/docs/topics/voice-connections#voice-data-interpolation
                last_timestamp = packet.timestamp
                continue

            if last_timestamp is not None:
                elapsed = (packet.timestamp - last_timestamp) / Decoder.SAMPLING_RATE
                if elapsed > 0.02:
                    # 無音期間
                    margin = [0] * 2 * int(Decoder.SAMPLE_SIZE * (elapsed - 0.02) * Decoder.SAMPLING_RATE)
                    pcm += margin

            data = decoder.decode_float(packet.decrypted)
            pcm += data
            last_timestamp = packet.timestamp

        del decoder

        return dict(data=pcm, start_time=start_time)

    async def decode(self):
        file = BytesIO()
        wav = wave.open(file, "wb")
        wav.setnchannels(Decoder.CHANNELS)
        wav.setsampwidth(Decoder.SAMPLE_SIZE // Decoder.CHANNELS)
        wav.setframerate(Decoder.SAMPLING_RATE)
        pcm_list = []

        for ssrc in self.queue.get_all_ssrc():
            pcm_list.append(await self._decode(ssrc))

        pcm_list.sort(key=lambda x: x["start_time"])

        if not pcm_list:
            # 音声がなかった場合
            wav.close()
            file.seek(0)
            return file
        # 録音が始まった時刻
        first_time = pcm_list[0]["start_time"]
        for pcm in pcm_list:
            # 録音が始まった時刻からのマージンをつける
            pcm["data"] = [0] * int(48000 * 2 * (pcm["start_time"] - first_time)) + pcm["data"]

        right_channel = []
        left_channel = []

        i = 0
        for bytes_ in zip_longest(*map(lambda x: x["data"], pcm_list)):
            # 左右のチャンネルにそれぞれ音声を合成してから入れる処理
            result = 0
            for b in bytes_:
                if b is None:
                    continue
                # 音声の合成
                # result = x + y - (x * y * -1) when x < 0 and y < 0
                # result = x + y - (x * y) when x > 0 and y > 0
                # otherwise, result = x + y
                if result < 0 and b < 0:
                    result = result + b - (result * b * -1)
                elif result > 0 and b > 0:
                    result = result + b - (result * b)
                else:
                    result = result + b

            # クリッピングの対処
            if result > 1:
                if not i % 2:
                    right_channel.append(1)
                else:
                    left_channel.append(1)
            elif result < -1:
                if not i % 2:
                    right_channel.append(-1)
                else:
                    left_channel.append(-1)
            else:
                if not i % 2:
                    right_channel.append(result)
                else:
                    left_channel.append(result)
            i += 1

        # 左右のチャンネルの大きさが違う場合があるので、その場合の処理
        left_len = len(left_channel)
        right_len = len(right_channel)
        if left_len != right_len:
            if not left_len % 2:
                if left_len > right_len:
                    right_channel += [0] * (left_len - right_len)
                else:
                    right_channel = right_channel[:left_len]
            elif not right_len % 2:
                if right_len > left_len:
                    left_channel += [0] * (right_len - left_len)
                else:
                    left_channel = left_channel[:right_len]

        audio = np.array([left_channel, right_channel]).T

        # Convert to (little-endian) 16 bit integers.
        audio = (audio * (2 ** 15 - 1)).astype(np.int16)

        wav.writeframes(audio.tobytes())
        wav.close()
        file.seek(0)

        return file


class RTCPacket:
    def __init__(self, header, decrypted):
        self.version = (header[0] & 0b11000000) >> 6
        self.padding = (header[0] & 0b00100000) >> 5
        self.extend = (header[0] & 0b00010000) >> 4
        self.cc = header[0] & 0b00001111
        self.marker = header[1] >> 7
        self.payload_type = header[1] & 0b01111111
        self.offset = 0
        self.ext_length = None
        self.ext_header = None
        self.csrcs = None
        self.profile = None
        self.real_time = None

        self.header = header
        self.decrypted = decrypted
        self.seq, self.timestamp, self.ssrc = struct.unpack_from('>HII', header, 2)

    def set_real_time(self):
        self.real_time = time.time()

    def calc_extension_header_length(self) -> None:
        if not (self.decrypted[0] == 0xbe and self.decrypted[1] == 0xde and len(self.decrypted) > 4):
            return
        self.ext_length = int.from_bytes(self.decrypted[2:4], "big")
        offset = 4
        for i in range(self.ext_length):
            byte_ = self.decrypted[offset]
            offset += 1
            if byte_ == 0:
                continue
            offset += 1 + (0b1111 & (byte_ >> 4))

        # Discordの仕様
        if self.decrypted[offset + 1] in [0, 2]:
            offset += 1
        self.decrypted = self.decrypted[offset + 1:]


class MyVoiceWebSocket(DiscordVoiceWebSocket):
    def __init__(self, socket, loop, hook):
        super().__init__(socket, loop)
        self.record_ready = False

    async def received_message(self, msg):
        await super(MyVoiceWebSocket, self).received_message(msg)
        op = msg['op']

        if op == self.SESSION_DESCRIPTION:  # op 5
            self.record_ready = True


class MyVoiceClient(VoiceClient):
    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.record_task = None
        self.decoder = None
        self.is_recording = False

    async def recv_voice_packet(self):
        if not self.ws.record_ready:
            raise ValueError("Not Record Ready")

        while True:
            recv = await self.loop.sock_recv(self.socket, 2 ** 16)
            if 200 <= recv[1] < 205:
                continue
            decrypt_func = getattr(self, f'decrypt_{self.mode}')
            header, data = decrypt_func(recv)
            packet = RTCPacket(header, data)
            packet.set_real_time()
            packet.calc_extension_header_length()
            self.decoder.recv_packet(packet)

    async def connect_websocket(self) -> MyVoiceWebSocket:
        ws = await MyVoiceWebSocket.from_client(self)
        self._connected.clear()
        while ws.secret_key is None:
            await ws.poll_event()
        self._connected.set()
        return ws

    def decrypt_xsalsa20_poly1305(self, data: bytes) -> tuple:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        is_rtcp = 200 <= data[1] < 205
        if is_rtcp:
            header, encrypted = data[:8], data[8:]
            nonce = bytearray(24)
            nonce[:8] = header
        else:
            header, encrypted = data[:12], data[12:]
            nonce = bytearray(24)
            nonce[:12] = header
        return header, box.decrypt(bytes(encrypted), bytes(nonce))

    def decrypt_xsalsa20_poly1305_suffix(self, data: bytes) -> tuple:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        is_rtcp = 200 <= data[1] < 205
        if is_rtcp:
            header, encrypted, nonce = data[:8], data[8:-24], data[-24:]
        else:
            header, encrypted, nonce = data[:12], data[12:-24], data[-24:]
        return header, box.decrypt(bytes(encrypted), bytes(nonce))

    def decrypt_xsalsa20_poly1305_lite(self, data: bytes) -> tuple:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        is_rtcp = 200 <= data[1] < 205
        if is_rtcp:
            header, encrypted, _nonce = data[:8], data[8:-4], data[-4:]
        else:
            header, encrypted, _nonce = data[:12], data[12:-4], data[-4:]
        nonce = bytearray(24)
        nonce[:4] = _nonce
        return header, box.decrypt(bytes(encrypted), bytes(nonce))

    async def record(self, record_time=30):
        if self.is_recording:
            raise ValueError("Already recording")

        # init
        self.decoder = None
        self.is_recording = True
        self.decoder = BufferDecoder()

        # do record
        self.record_task = self.loop.create_task(self.recv_voice_packet())
        await asyncio.sleep(record_time)

        self.record_task.cancel()

        # clear data
        self.record_task = None
        self.is_recording = False
        return await self.decoder.decode()
