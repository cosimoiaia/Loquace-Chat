from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.behaviors.focus import FocusBehavior
from llama_cpp import Llama
from icecream.icecream import ic


class ChatApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.send_button = None
        self.user_input = None
        self.down_bar = None
        self.message_label = None
        self.layout = None
        self.llm = None
        self.history = []

    def build(self):
        # Load the gguf model
        self.llm = Llama(model_path="/home/mimmo/LLM/Loquace-7b-mistral-q8_0.gguf", n_threads=8)

        self.layout = GridLayout()
        self.layout.cols = 1
        # create message label
        self.message_label = Label(size_hint_y=0.9)
        self.layout.add_widget(self.message_label)

        # create text input field for user to enter messages
        self.down_bar = BoxLayout()
        self.user_input = TextInput(multiline=False, size_hint_y=0.1)
        self.user_input.bind(on_text_validate=self.send_message)
        self.down_bar.add_widget(self.user_input)

        # create send button
        self.send_button = Button(text="Send", size_hint_y=0.1, size_hint_x=0.2)
        self.send_button.bind(on_press=self.send_message)
        self.down_bar.add_widget(self.send_button)

        self.layout.add_widget(self.down_bar)

        return self.layout

    def send_message(self, instance):
        """Handle sending of messages."""
        message = self.user_input.text
        if not message:
            return

        # add message to the UI
        self.message_label.text += "\nYou: " + message

        # generate a response from the LLM
        self.history.append({"role": "user", "content": message})
        output = self.llm.create_chat_completion(messages=self.history,
                                                 max_tokens=64, temperature=0.2)
        ic(output)

        # Update label with response
        self.message_label.text += "\nLoquace: " + output['choices'][0]['message']['content']
        self.history.append(output['choices'][0]['message'])

        # clear the input field
        self.user_input.text = ""

    def on_start(self):
        # Focus the text input field when the app starts
        Window.bind(on_key_down=self.on_key_down)
        self.user_input.focus = True

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        # If the 'enter' key is pressed, send the message
        if keycode == 40:
            self.send_message(self.user_input)
            # Get always the focus back on the text input
            self.user_input.focus = True
            FocusBehavior.focus = True


if __name__ == "__main__":
    app = ChatApp()
    app.run()
