#!/usr/bin/env python3
"""The CBC padding oracle"""

from base64 import b64decode

from Crypto.Random.random import getrandbits, randint

from m09 import pkcs7
from m10 import encrypt_aes_cbc, decrypt_aes_cbc
from m15 import de_pkcs7

RANDOM_KEY = bytes(getrandbits(8) for i in range(16))
IV = bytes(getrandbits(8) for i in range(16))

def chose_plaintext() -> bytes:
    with open("data/17.txt", "r") as f:
        data = f.read().splitlines()
    return pkcs7(b64decode(data[randint(0, len(data) - 1)]))

def cbc_oracle() -> bytes:
    plaintext = chose_plaintext()
    return encrypt_aes_cbc(plaintext, RANDOM_KEY, IV)

def padding_oracle(cyphertext: bytes) -> bool:
    key = RANDOM_KEY
    iv = IV
    plaintext = decrypt_aes_cbc(cyphertext, key, iv)
    pad_length = plaintext[-1]
    return pad_length * bytes([pad_length]) == plaintext[-pad_length:]

def attack_block(block: int, cyphertext: bytes) -> bytes:
    c = [cyphertext[i:i + 16] for i in range(0, len(cyphertext), 16)]
    c_prime = bytearray(16)
    p = bytearray(16)

    for i in range(15, -1, -1):
        for b in range(256):
            c_prime[i] = b
            if padding_oracle(bytes(c_prime) + c[block]):
                print("block", str(block) + ": c' =", c_prime.hex()
                      + ", p =", p.hex(), end="\r")
                if i == 15:
                    c_test = c_prime
                    c_test[i - 1] ^= c_prime[i]
                    if padding_oracle(bytes(c_test) + c[block]):
                        break
                else:
                    break

        p[i] = (16 - i) ^ c_prime[i] ^ c[block - 1][i]

        for j in range(i, 16):
            c_prime[j] = c_prime[j] ^ (16 - i) ^ (16 - i + 1)

    print()
    return bytes(p)

def attack(c: bytes) -> bytes:
    p = [attack_block(i, c) for i in range(len(c) // 16 - 1, 0, -1)]
    return de_pkcs7(b"".join(p[::-1]))

def main() -> None:
    cyphertext = cbc_oracle()
    print("[" + 14 * "_" + "]" + attack(cyphertext).decode())

if __name__ == "__main__":
    main()
