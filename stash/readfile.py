total = b""
with open("test.md", "rb") as f:
    byte = f.read(32756)
    while byte != b"":
        # Do stuff with byte.
        total += byte
        byte = f.read(32756)


# print(total)
print(len(total))
print(total.hex())
