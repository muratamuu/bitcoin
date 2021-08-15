import hashlib

def hash160(s):
    '''sha256 の後にripemd160が続く'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()
