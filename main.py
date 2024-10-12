from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from utils.encryption import encrypt_files, decrypt_files
from ui.settings import SettingsDialog
from ui.dialogs import show_message

class EncryptedVolumeApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.file_chooser = FileChooserListView()
        self.layout.add_widget(self.file_chooser)
        
        self.settings_button = Button(text='Налаштування', size_hint_y=None, height=50)
        self.settings_button.bind(on_press=self.open_settings)
        self.layout.add_widget(self.settings_button)

        self.encrypt_button = Button(text='Шифрувати', size_hint_y=None, height=50)
        self.encrypt_button.bind(on_press=self.encrypt_files)
        self.layout.add_widget(self.encrypt_button)

        self.decrypt_button = Button(text='Розшифрувати', size_hint_y=None, height=50)
        self.decrypt_button.bind(on_press=self.decrypt_files)
        self.layout.add_widget(self.decrypt_button)

        return self.layout

    def open_settings(self, instance):
        dialog = SettingsDialog()
        dialog.open()

    def encrypt_files(self, instance):
        selected_files = self.file_chooser.selection
        if not selected_files:
            show_message("Будь ласка, виберіть файл для шифрування.")
            return
        key = b'your_secret_key'  # Заміни на власний ключ
        method = 'AES'  # Метод шифрування
        encrypt_files(selected_files, key, method)
        show_message("Файли успішно зашифровані.")

    def decrypt_files(self, instance):
        selected_files = self.file_chooser.selection
        if not selected_files:
            show_message("Будь ласка, виберіть файл для розшифрування.")
            return
        key = b'your_secret_key'  # Заміни на власний ключ
        method = 'AES'  # Метод шифрування
        decrypt_files(selected_files, key, method)
        show_message("Файли успішно розшифровані.")

if __name__ == '__main__':
    EncryptedVolumeApp().run()
