import os
import socket
import threading
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from tqdm import tqdm

# Конфігурація для передачі файлів
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_PORT = 5001

class FileTransferApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Кнопка "Я отримувач"
        receiver_button = Button(text='Я отримувач', size_hint=(1, 0.5))
        receiver_button.bind(on_press=self.start_receiver)

        # Кнопка "Я відправник"
        sender_button = Button(text='Я відправник', size_hint=(1, 0.5))
        sender_button.bind(on_press=self.select_file)

        layout.add_widget(receiver_button)
        layout.add_widget(sender_button)

        return layout

    def start_receiver(self, instance):
        threading.Thread(target=self.run_receiver, daemon=True).start()

        popup = Popup(title='Отримувач',
                      content=Label(text='Очікування на файл...'),
                      size_hint=(0.8, 0.8))
        popup.open()

    def run_receiver(self):
        # Отримання локальної IP-адреси пристрою
        local_ip = socket.gethostbyname(socket.gethostname())
        print(f"Очікування з'єднання на {local_ip}:{SERVER_PORT}...")

        # Запуск сервера для приймання файлів
        server_socket = socket.socket()
        server_socket.bind((local_ip, SERVER_PORT))
        server_socket.listen(1)

        client_socket, address = server_socket.accept()
        print(f"З'єднання з {address}")

        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)

        # Прогрес отримання
        progress = tqdm(range(filesize), f"Отримання {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
                progress.update(len(bytes_read))

        client_socket.close()
        server_socket.close()
        print(f"Файл {filename} отримано успішно!")

    def select_file(self, instance):
        # Вибір файлу для відправлення
        filechooser = FileChooserIconView()
        popup = Popup(title='Виберіть файл',
                      content=filechooser,
                      size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=self.send_file)
        popup.open()

    def send_file(self, filechooser, selection, *args):
        filepath = selection[0]
        filesize = os.path.getsize(filepath)
        ip_input = 'Введіть IP отримувача в локальній мережі: '
        receiver_ip = input(ip_input)  # Введення IP-адреси отримувача

        threading.Thread(target=self.run_sender, args=(filepath, filesize, receiver_ip), daemon=True).start()

    def run_sender(self, filepath, filesize, receiver_ip):
        # Підключення до отримувача і передача файлу
        client_socket = socket.socket()
        client_socket.connect((receiver_ip, SERVER_PORT))

        # Відправляємо файл
        client_socket.send(f"{filepath}{SEPARATOR}{filesize}".encode())

        progress = tqdm(range(filesize), f"Надсилання {filepath}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filepath, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
                progress.update(len(bytes_read))

        client_socket.close()
        print(f"Файл {filepath} успішно надіслано!")

if __name__ == '__main__':
    FileTransferApp().run()
