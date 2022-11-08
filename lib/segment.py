from struct import *

# Constants
NULL_FLAG = 0b00000000
FIN_FLAG = 0b00000001
SYN_FLAG = 0b00000010
ACK_FLAG = 0b00010000
SYN_ACK = SYN_FLAG + ACK_FLAG
FLAGS = {
    NULL_FLAG: "NULL_FLAG",
    SYN_FLAG: "SYN_FLAG",
    ACK_FLAG: "ACK_FLAG",
    FIN_FLAG: "FIN_FLAG",
    SYN_ACK: "SYN_ACK",
}


# Segments
class SegmentFlag:
    def __init__(self, flag: bytes):
        # Init flag variable from flag byte
        self.flag = flag

    def __str__(self) -> str:
        to_bin = int(self.flag.decode(), 2)
        return FLAGS[to_bin]

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        return self.flag

    @staticmethod
    def flag_to_byte(flag: str):
        return format(flag, "08b").encode()


class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        pass

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        output += f"{'Sequence number':24} | {self.seq_num}\n"
        output += f"{'Acknowledgement number':24} | {self.ack_num}\n"
        output += f"{'Flag number':24} | {str(self.flag)}\n"
        output += f"{'Checksum':24} | {self.checksum}\n"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        return 1  # STUB

    # -- Setter --
    def set_header(self, header: dict):
        self.seq_num = header["seq_num"]
        self.ack_num = header["ack_num"]
        self.flag = SegmentFlag(header["flag"])  # pasti bytes
        self.checksum = header["checksum"]

    def set_payload(self, payload: bytes):
        self.payload = payload

    def set_flag(self, flag_list: list):
        tmp = 0
        for flag in flag_list:
            tmp += flag
        self.flag = SegmentFlag(tmp)

    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        return self.flag

    def get_header(self) -> dict:
        return {
            "seq_num": self.seq_num,
            "ack_num": self.ack_num,
            "flag": self.flag,
            "checksum": self.checksum,
        }

    def get_payload(self) -> bytes:
        return self.payload

    # -- Marshalling --
    def set_from_bytes(self, src: bytes):
        # From pure bytes, unpack() and set into python variable
        (self.seq_num, self.ack_num, tmp, self.checksum, self.payload) = unpack(
            "<ii8sxh32756s", src
        )
        self.flag = SegmentFlag(tmp)

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        return pack(
            "<ii8sxh32756s",
            self.seq_num,
            self.ack_num,
            self.flag.get_flag_bytes(),
            self.checksum,
            self.payload,
        )

    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        return self.__calculate_checksum() == self.checksum


if __name__ == "__main__":
    header = {
        "seq_num": 2,
        "ack_num": 3,
        "flag": SegmentFlag.flag_to_byte(SYN_FLAG),
        "checksum": 1,
    }
    data = b"capek kuliah"
    seg = Segment()
    seg.set_header(header)
    seg.set_payload(data)
    print(seg)

    # Simulate sending
    sender = seg.get_bytes()
    recv = Segment()
    recv.set_from_bytes(sender)
    print(recv)
