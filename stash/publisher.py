from lib.connection import *
from lib.segment import *

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


client = Connection("localhost", 3000)
client.send_data(msg=seg, dest=("localhost", 8080))
