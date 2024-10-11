import os
import socket
import threading
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from tqdm import tqdm

# Конфігурація для передачі файлів
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_PORT = 5001
BROADCAST_PORT = 5002

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

    # Функція для старту отримувача
    def start_receiver(self, instance):
        threading.Thread(target=self.listen_for_sender, daemon=True).start()

        popup = Popup(title='Отримувач',
                      content=Label(text='Очікування на файл...'),
                      size_hint=(0.8, 0.8))
        popup.open()

    # Слухач для отримувача
    def listen_for_sender(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.bind(('', BROADCAST_PORT))

        print("Очікування мовлення від відправника...")
        while True:
            message, address = udp_socket.recvfrom(1024)
            if message.decode() == 'FIND_RECEIVER':
                print(f"Відправник знайдено на {address}")
                udp_socket.sendto('RECEIVER_FOUND'.encode(), address)

                # Приймаємо файл через TCP
                threading.Thread(target=self.receive_file, args=(address[0],), daemon=True).start()

    # Прийом файлу
    def receive_file(self, sender_ip):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(('', SERVER_PORT))
        tcp_socket.listen(1)
        print(f"Очікування з'єднання на {sender_ip}:{SERVER_PORT}...")

        client_socket, _ = tcp_socket.accept()
        print("З'єднання встановлено!")

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
        tcp_socket.close()
        print(f"Файл {filename} отримано успішно!")

    # Вибір файлу для відправника
    def select_file(self, instance):
        filechooser = FileChooserIconView()
        popup = Popup(title='Виберіть файл',
                      content=filechooser,
                      size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=self.find_receiver)
        popup.open()

    # Пошук отримувача через UDP
    def find_receiver(self, filechooser, selection, *args):
        filename = selection[0]
        threading.Thread(target=self.broadcast_and_send, args=(filename,), daemon=True).start()

    # Мовлення UDP і відправка файлу
    def broadcast_and_send(self, filename):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print("Пошук отримувача...")
        udp_socket.sendto('FIND_RECEIVER'.encode(), ('<broadcast>', BROADCAST_PORT))

        udp_socket.settimeout(5)
        try:
            message, address = udp_socket.recvfrom(1024)
            if message.decode() == 'RECEIVER_FOUND':
                print(f"Отримувач знайдено на {address[0]}")
                self.send_file(filename, address[0])
        except socket.timeout:
            print("Отримувача не знайдено.")

        udp_socket.close()

    # Відправка файлу через TCP
    def send_file(self, filename, receiver_ip):
        filesize = os.path.getsize(filename)
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((receiver_ip, SERVER_PORT))

        # Відправляємо метадані про файл
        tcp_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

        # Прогрес передачі
        progress = tqdm(range(filesize), f"Надсилання {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                tcp_socket.sendall(bytes_read)
                progress.update(len(bytes_read))

        tcp_socket.close()
        print(f"Файл {filename} успішно надіслано!")

if __name__ == '__main__':
    FileTransferApp().run()
