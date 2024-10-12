from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

class SettingsPopup(Popup):
    def __init__(self, store, **kwargs):
        super(SettingsPopup, self).__init__(title='Settings', size_hint=(None, None), size=(400, 300), **kwargs)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Require password on startup'))

        self.store = store
        self.password_checkbox = CheckBox(active=self.store.get('require_password')['value'] if self.store.exists('require_password') else False)
        layout.add_widget(self.password_checkbox)

        password_button = Button(text='Set Password')
        password_button.bind(on_press=self.set_password)
        layout.add_widget(password_button)

        save_button = Button(text='Save Settings')
        save_button.bind(on_press=self.save_settings)
        layout.add_widget(save_button)

        self.content = layout

    def set_password(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.new_password_input = TextInput(hint_text='Enter new password', multiline=False, password=True)
        layout.add_widget(self.new_password_input)

        confirm_button = Button(text='Confirm')
        confirm_button.bind(on_press=self.save_new_password)
        layout.add_widget(confirm_button)

        popup = Popup(title='Set Password', content=layout, size_hint=(None, None), size=(400, 200))
        popup.open()

    def save_new_password(self, instance):
        new_password = self.new_password_input.text
        if new_password:  # Перевірка на непорожній пароль
            self.store.put('password', value=new_password)  # Зберігаємо новий пароль
            self.dismiss()  # Закрити спливаюче вікно
        else:
            self.show_popup("Error", "Password cannot be empty!")

    def save_settings(self, instance):
        require_password = self.password_checkbox.active
        self.store.put('require_password', value=require_password)  # Зберігаємо налаштування
        self.dismiss()  # Закрити спливаюче вікно

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()
