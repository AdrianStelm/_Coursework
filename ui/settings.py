from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.spinner import Spinner
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
import os

class EncryptedVolumeApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Розділ для створення зашифрованого тому
        self.size_input = TextInput(hint_text='Enter volume size in MB', multiline=False)
        layout.add_widget(self.size_input)

        # Додано FileChooser для вибору шляху збереження
        self.file_chooser = FileChooserListView()
        layout.add_widget(self.file_chooser)

        self.password_input = TextInput(hint_text='Enter encryption password', multiline=False)
        layout.add_widget(self.password_input)

        self.create_button = Button(text='Create Encrypted Volume')
        self.create_button.bind(on_press=self.create_volume)
        layout.add_widget(self.create_button)

        # Розділ для шифрування/дешифрування файлів
        self.file_chooser_encrypt = FileChooserListView()
        layout.add_widget(self.file_chooser_encrypt)

        self.spinner = Spinner(
            text='Choose encryption method',
            values=('AES', 'DES'),
            size_hint=(None, None), size=(200, 44))
        layout.add_widget(self.spinner)

        self.key_input = TextInput(hint_text='Enter encryption key', multiline=False)
        layout.add_widget(self.key_input)

        self.encrypt_button = Button(text='Encrypt Files')
        self.encrypt_button.bind(on_press=self.encrypt_files)
        layout.add_widget(self.encrypt_button)

        self.decrypt_button = Button(text='Decrypt Files')
        self.decrypt_button.bind(on_press=self.decrypt_files)
        layout.add_widget(self.decrypt_button)

        return layout

    def create_volume(self, instance):
        size = self.size_input.text
        path = self.file_chooser.selection[0] if self.file_chooser.selection else ""
        password = self.password_input.text
        
        if not size or not path or not password:
            self.show_popup("Error", "All fields are required!")
            return
        
        try:
            size_mb = int(size)
            size_bytes = size_mb * 1024 * 1024
            # Create a file of specified size
            with open(path, 'wb') as f:
                f.write(os.urandom(size_bytes))
            
            # Encrypt the created file
            key = self.prepare_key(password)
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            with open(path, 'r+b') as f:
                plaintext = f.read()
                ciphertext = encryptor.update(plaintext) + encryptor.finalize()
                f.seek(0)
                f.write(iv + ciphertext)  # Prepend IV to the file
            
            self.show_popup("Success", f"Encrypted volume created at {path}")

        except Exception as e:
            self.show_popup("Error", str(e))

    def encrypt_files(self, instance):
        selected_files = self.file_chooser_encrypt.selection
        if not selected_files:
            self.show_popup("Error", "No file selected!")
            return

        key = self.key_input.text
        if not key:
            self.show_popup("Error", "Please enter a key!")
            return

        if self.spinner.text == 'AES':
            key = self.prepare_key(key, length=32)
            iv = os.urandom(16)
            encryptor = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend()).encryptor()
        else:
            key = self.prepare_key(key, length=8)
            iv = os.urandom(8)
            encryptor = Cipher(algorithms.DES(key), modes.CFB(iv), backend=default_backend()).encryptor()

        for file_path in selected_files:
            with open(file_path, 'rb') as f:
                plaintext = f.read()

            ciphertext = encryptor.update(plaintext) + encryptor.finalize()

            # Генеруємо HMAC для контролю правильності дешифрування
            h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
            h.update(ciphertext)
            hmac_digest = h.finalize()

            # Додаємо спеціальний заголовок "ENCRYPTED" для зашифрованого файлу
            header = b"ENCRYPTED"

            # Створюємо зашифрований файл
            new_file_path = f"{file_path}.enc"
            with open(new_file_path, 'wb') as f:
                f.write(header + iv + ciphertext + hmac_digest)  # Додаємо заголовок, IV і HMAC до файлу

            self.show_popup("Success", f"Files successfully encrypted! Saved as {new_file_path}")

    def decrypt_files(self, instance):
        selected_files = self.file_chooser_encrypt.selection
        if not selected_files:
            self.show_popup("Error", "No file selected!")
            return

        key = self.key_input.text
        if not key:
            self.show_popup("Error", "Please enter a key!")
            return

        if self.spinner.text == 'AES':
            key = self.prepare_key(key, length=32)
            block_size = 16
        else:
            key = self.prepare_key(key, length=8)
            block_size = 8

        for file_path in selected_files:
            with open(file_path, 'rb') as f:
                header = f.read(9)  # Читаємо перші 9 байт (довжина "ENCRYPTED")
                
                # Перевіряємо, чи файл зашифрований
                if header != b"ENCRYPTED":
                    self.show_popup("Error", "This file is not encrypted!")
                    return
                
                iv = f.read(block_size)
                data = f.read()  # Читаємо решту файлу

                # Відокремлюємо зашифрований контент та HMAC
                ciphertext = data[:-32]  # Все, крім останніх 32 байт, це зашифровані дані
                hmac_stored = data[-32:]  # Останні 32 байти — це збережений HMAC

            # Ініціалізуємо дешифратор
            decryptor = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend()).decryptor() if self.spinner.text == 'AES' else Cipher(algorithms.DES(key), modes.CFB(iv), backend=default_backend()).decryptor()

            try:
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()

                # Перевіряємо HMAC
                h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
                h.update(ciphertext)
                h.verify(hmac_stored)  # Перевіряємо, чи співпадає HMAC

                # Зберігаємо розшифрований файл
                file_name, file_extension = os.path.splitext(file_path)
                original_file_path = f"{file_name}_decrypted{file_extension}"
                with open(original_file_path, 'wb') as f:
                    f.write(plaintext)

                self.show_popup("Success", f"Files successfully decrypted! Saved as {original_file_path}")
            except Exception as e:
                self.show_popup("Error", "Invalid key or corrupted file! Cannot decrypt.")

    def prepare_key(self, key, length=32):
        # Підгонка ключа до потрібної довжини
        key_bytes = key.encode('utf-8')
        if len(key_bytes) < length:
            return key_bytes.ljust(length, b'\0')
        return key_bytes[:length]

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == '__main__':
    EncryptedVolumeApp().run()  