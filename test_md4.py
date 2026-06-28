from Crypto.Hash import MD4
h = MD4.new(b"test")
print("MD4 available:", h.hexdigest())