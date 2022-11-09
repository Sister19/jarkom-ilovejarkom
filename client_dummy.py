from lib import connection as conn
from lib import segment as seg

header = {
    "seq_num": 2,
    "ack_num": 3,
    "flag": seg.SegmentFlag.uint_to_byte(seg.SYN_FLAG),
    "checksum": 1,
}
data = b"capek kuliah" + b"a" * 32744 + b"overflow"
seg = seg.Segment()
seg.set_header(header)
seg.set_payload(data)


client = conn.Connection("localhost", 3000)
client.send_data(msg=seg, dest=("localhost", 8080))
