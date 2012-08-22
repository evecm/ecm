# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = '2012 08 01'
__author__ = 'diabeteman'

import base64

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

PADDING = '#'
BLOCK_SIZE = 32
RSA_KEY_SIZE = 2048

def pad(s):
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

def aes_encrypt(secret, plain_text):
    cipher = AES.new(secret)
    cipher_text = cipher.encrypt(pad(plain_text))
    return base64.b64encode(cipher_text)

def aes_decrypt(secret, cipher_text):
    cipher = AES.new(secret)
    cipher_text = base64.b64decode(cipher_text)
    return cipher.decrypt(cipher_text).strip(PADDING)

def extract_public_key(private_key_str):
    private_key = RSA.importKey(private_key_str)
    return private_key.publickey().exportKey()

def key_fingerprint(key_str):
    return SHA256.new(key_str).hexdigest()

def rsa_encrypt(public_key_str, plain_text):
    public_key = RSA.importKey(public_key_str)
    encrypted_secret, = public_key.encrypt(plain_text, 0)
    return base64.b64encode(encrypted_secret)

def rsa_decrypt(private_key_str, cipher_text):
    private_key = RSA.importKey(private_key_str)
    return private_key.decrypt(base64.b64decode(cipher_text))

def generate_secret(n_bytes=BLOCK_SIZE):
    return Random.get_random_bytes(n_bytes)

def generate_rsa_keypair():
    return RSA.generate(RSA_KEY_SIZE, Random.new().read).exportKey()
