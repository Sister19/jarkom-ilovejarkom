from dataclasses import dataclass
from struct import *
from typing import List

from lib.flags import *

MAX_PAYLOAD = 32756


@dataclass
class SegmentFlag:
    value: int

    def __str__(self) -> str:
        return FLAGS[self.value]


@dataclass
class SegmentHeader:
    seq_num: int
    ack_num: int
    flag: List[int]


class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        pass

    def __str__(self):
        output = ""
        output += f"{'Sequence number':24} | {self.seq_num}\n"
        output += f"{'Acknowledgement number':24} | {self.ack_num}\n"
        output += f"{'Flag number':24} | {str(self.flag)}\n"
        output += f"{'Checksum':24} | {self.checksum}\n"
        output += f"{'Payload':24} | {self.payload.decode()}"
        return output

    # -- Setter --
    def set_header(self, header: SegmentHeader):
        self.seq_num = header.seq_num
        self.ack_num = header.ack_num
        self.set_flag(header.flag)

    def set_payload(self, payload: bytes):
        self.payload = payload

    def set_flag(self, flag_list: list):
        tmp = 0
        for flag in flag_list:
            tmp += flag
        self.flag = SegmentFlag(tmp)

    def set_checksum(self):
        self.checksum = self.__calculate_checksum()

    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        return self.flag

    def get_header(self) -> SegmentHeader:
        return SegmentHeader(seq_num=self.seq_num, ack_num=self.ack_num, flag=self.flag)

    def get_payload(self) -> bytes:
        return self.payload

    # -- Marshalling --
    def set_from_bytes(self, src: bytes):
        # From pure bytes, unpack() and set into python variable
        (self.seq_num, self.ack_num, tmp, self.checksum, self.payload) = unpack(
            f"<iiBxh{MAX_PAYLOAD}s", src
        )
        self.flag = SegmentFlag(tmp)

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        return pack(
            f"<iiBxh{MAX_PAYLOAD}s",
            self.seq_num,
            self.ack_num,
            self.flag.value,
            self.checksum,
            self.payload,
        )

    # -- Checksum --
    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        return 1  # STUB

    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        return self.__calculate_checksum() == self.checksum

    # -- Builder --
    def build(self, header: SegmentHeader, payload: bytes):
        self.set_header(header)
        self.set_payload(payload)
        self.set_checksum()
        return self

    def build_from_bytes(self, bytes_data: bytes):
        self.set_from_bytes(bytes_data)
        self.set_checksum()
        return self


if __name__ == "__main__":
    header = SegmentHeader(
        seq_num=3,
        ack_num=1,
        flag=[SYN_FLAG, ACK_FLAG],
    )
    data = b"capek kuliah"
    seg = Segment()
    seg.set_header(header)
    seg.set_payload(data)
    print(seg)
    print(len(seg.get_bytes()))

    # Simulate sending
    seg_sender = seg.get_bytes()
    recv = Segment()
    recv.set_from_bytes(seg_sender)
    print(recv)
    print(len(recv.get_bytes()))
