from struct import *

# p = pack("<hhf", 1, 2, 3.0)  # hhf = short, short, float
# # (in Python: int, int, float)
# print(p)  # value will be bytes
# print(type(p))

# up = unpack("<hhf", p)
# print(up)  # decode back bytes to (int, int, float)
# print(type(up))

# print(type(up[0]))
# print(type(up[1]))
# print(type(up[2]))


seg = pack(
    "<ii8sxh32756s",
    1,  # seqnum
    2,  # acknum
    b"00000001",  # flag
    4,  # checksum
    ("halooo").encode(),  # payload
)
# print(seg)

segup = unpack("<ii8sxh32756s", seg)
# print(segup)

msg = segup[-1]
print(msg.decode())
