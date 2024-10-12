from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

def show_popup(title, message):
    layout = BoxLayout(orientation='vertical', padding=10)
    label = Label(text=message)
    close_button = Button(text="Close")
    layout.add_widget(label)
    layout.add_widget(close_button)
    
    popup = Popup(title=title, content=layout, size_hint=(None, None), size=(400, 200))
    close_button.bind(on_press=popup.dismiss)
    popup.open()
