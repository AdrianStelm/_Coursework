from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.storage.jsonstore import JsonStore
from ui.main_layout import MainLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

class EncryptedVolumeApp(App):
    def build(self):
        self.store = JsonStore('settings.json')

        # Перевірка наявності пароля
        if self.store.exists('require_password') and self.store.get('require_password')['value']:
            return self.show_password_popup()
        
        return MainLayout(self.store)

    def show_password_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.password_input = TextInput(hint_text='Enter password', multiline=False, password=True)
        layout.add_widget(self.password_input)

        submit_button = Button(text='Submit')
        submit_button.bind(on_press=self.check_password)
        layout.add_widget(submit_button)

        return layout

    def check_password(self, instance):
        saved_password = self.store.get('password')['value'] if self.store.exists('password') else ''
        
        # Перевірка введеного пароля
        if self.password_input.text == saved_password:
            self.root.clear_widgets()
            self.root.add_widget(MainLayout(self.store))
        else:
            self.show_popup("Error", "Invalid password!")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == '__main__':
    EncryptedVolumeApp().run()