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
        output += f"{'Payload':24} | {self.payload}"
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
        dynamic_size = len(src) - 12

        (self.seq_num, self.ack_num, tmp, self.checksum, self.payload) = unpack(
            f"<iiBxH{dynamic_size}s", src
        )
        self.flag = SegmentFlag(tmp)

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        dynamic_size = len(self.payload)
        return pack(
            f"<iiBxH{dynamic_size}s",
            self.seq_num,
            self.ack_num,
            self.flag.value,
            self.checksum,
            self.payload,
        )

    # -- Checksum --
    def __add_number(self,number1,number2):
        # This function is used in calculate checksum, handle if the sum of 2 numbers has a carry
        # If the sum does have a carry in front, then remove the carry and add it to the back of the integer
        result = (number1 + number2) & 0xFFFF
        result += (number1 + number2) >> 16
        return result

    def __calculate_checksum(self, complement = True) -> int:
        # Calculate checksum here, return checksum result
        # Using 16-bit one complement checksum
        checksum = 0

        # Sum the seq number first, group byte offset 0 1 and 2 3 to make it 16 bit
        left_seqNum = (self.seq_num & 0xFFFF0000) >> 16
        right_seqNum = (self.seq_num & 0x0000FFFF) 
        checksum = self.__add_number(checksum,left_seqNum)
        checksum = self.__add_number(checksum,right_seqNum)

        # Do the same for the ack number
        left_ackNum = (self.ack_num & 0xFFFF0000) >> 16
        right_ackNum = (self.ack_num & 0x0000FFFF) 
        checksum = self.__add_number(checksum,left_ackNum)
        checksum = self.__add_number(checksum,right_ackNum)

        # For the flag byte, augment with empty padding which is 0
        flag_Byte = (self.flag.value) << 8
        checksum = self.__add_number(checksum, flag_Byte)

        # Sum for all data in payload
        for i in range (0,len(self.payload),2):
            payload_bytes = self.payload[i:i+2]
            data_to_integer = int.from_bytes(payload_bytes, "big")
            if len(payload_bytes) == 2: # sudah 16 bits
                data_to_integer = int.from_bytes(payload_bytes, "big")
            else : # 8 bits aja, maka padding
                data_to_integer = (int.from_bytes(payload_bytes, "big")) << 8
            checksum = self.__add_number(checksum, data_to_integer)

        # To complement it
        if complement:
            checksum = 0xFFFF - checksum

        return checksum

    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        return self.__calculate_checksum(complement = False) + self.checksum == 0xFFFF

    # -- Builder --
    def build(self, header: SegmentHeader, payload: bytes):
        self.set_header(header)
        self.set_payload(payload)
        self.set_checksum()
        return self

    def build_from_bytes(self, bytes_data: bytes):
        self.set_from_bytes(bytes_data)
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
    seg.set_checksum()

    # Simulate sending
    seg_sender = seg.get_bytes()
    recv = Segment()
    recv.set_from_bytes(seg_sender)
    print(recv)
    print(len(recv.get_bytes()))
