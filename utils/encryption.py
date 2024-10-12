import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import hmac

def encrypt_files(file_paths, key, method):
    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            plaintext = f.read()

        # Шифрування
        iv = os.urandom(16)  # Генерація ініціалізаційного вектора
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Запис зашифрованого файлу
        with open(file_path + '.enc', 'wb') as f:
            f.write(iv + ciphertext)

        # Генерація HMAC
        h = hmac.new(key, msg=ciphertext, digestmod=hashes.SHA256())
        with open(file_path + '.hmac', 'wb') as f:
            f.write(h.digest())

def decrypt_files(file_paths, key, method):
    for file_path in file_paths:
        if not file_path.endswith('.enc'):
            continue
        
        with open(file_path, 'rb') as f:
            iv = f.read(16)  # Зчитування IV
            ciphertext = f.read()  # Зчитування зашифрованого тексту

        # Дешифрування
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Запис розшифрованого файлу
        with open(file_path[:-4], 'wb') as f:
            f.write(plaintext)

        # Перевірка HMAC (необов'язково)
        # with open(file_path + '.hmac', 'rb') as f:
        #     hmac_value = f.read()
        #     h = hmac.new(key, msg=ciphertext, digestmod=hashes.SHA256())
        #     if hmac_value != h.digest():
        #         raise ValueError("HMAC перевірка не вдалася.")
