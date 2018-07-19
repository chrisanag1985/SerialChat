from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


class AESEncDec:

    def __init__(self):

        self.BS = 32
        self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        self.unpad = lambda s: s[0:-ord(s[-1])]
        self.mode = AES.MODE_CBC

    def encrypt(self,key=None,text=None):

        iv = Random.get_random_bytes(16)
        text = self.pad(text)
        hash_key = SHA256.new(key).digest()
        enc = AES.new(hash_key,self.mode,iv).encrypt(text)
        return (iv+enc).encode('hex')

    def decrypt(self,key=None,encrypted_text=None):
        encrypted_text = encrypted_text.decode('hex')
        iv = encrypted_text[:16]
        en_txt = encrypted_text[16:]
        hash_key = SHA256.new(key).digest()
        dec = AES.new(hash_key,self.mode,iv).decrypt(en_txt)
        dec = self.unpad(dec)
        return dec

