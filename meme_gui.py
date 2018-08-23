from meme import Meme
from PIL import ImageTk
from Tkinter import *
import tkFileDialog
import ttk

import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton


def null_callback():
    pass


class HAlignSelect(GridLayout):
    idx = 0

    def __init__(self, align_changed_callback=null_callback, **kwargs):
        super(HAlignSelect, self).__init__(**kwargs)
        self.align_changed_callback = align_changed_callback
        self.cols = 3
        self.size_hint = (1.0, 0.125)
        self.buttons = list()
        self.buttons.append(
            ToggleButton(text='Left', group='halign' + str(HAlignSelect.idx)))
        self.buttons[-1].bind(on_press=self.on_align_changed)
        self.buttons.append(
            ToggleButton(
                text='Center',
                group='halign' + str(HAlignSelect.idx),
                state='down'))
        self.buttons[-1].bind(on_press=self.on_align_changed)
        self.buttons.append(
            ToggleButton(text='Right', group='halign' + str(HAlignSelect.idx)))
        self.buttons[-1].bind(on_press=self.on_align_changed)
        for button in self.buttons:
            self.add_widget(button)
        HAlignSelect.idx = HAlignSelect.idx + 1

    def align(self):
        align = [x for x in self.buttons if x.state == 'down']
        return align[0].text.lower()

    def on_align_changed(self, source):
        align = [x.text.lower() for x in self.buttons if x.state == 'down']
        if len(align) != 0:
            self.align_changed_callback(align[0])


class MemeTextBox(GridLayout):
    def __init__(self, text_changed_callback, **kwargs):
        super(MemeTextBox, self).__init__(**kwargs)
        self.text_changed_callback = text_changed_callback
        self.rows = 2
        self.align = HAlignSelect(self.on_align_changed)
        self.add_widget(self.align)
        self.input = TextInput(text='top', multiline=False, write_tab=False)
        self.input.bind(text=self.on_text_changed)
        self.add_widget(self.input)

    def on_text_changed(self, instance, value):
        align = self.align.align()
        self.text_changed_callback(value, align)

    def on_align_changed(self, align):
        self.text_changed_callback(self.input.text, align)


class MemeAppMainView(GridLayout):
    def __init__(self, main_app, **kwargs):
        super(MemeAppMainView, self).__init__(**kwargs)
        self.main_app = main_app
        self.cols = 2

        self.text_grid = GridLayout(rows=5, size_hint_x=None, width=400)

        self.load_button = Button(text='Select Image', size_hint=(1.0, 0.25))
        self.load_button.bind(on_press=self.select_image)

        self.save_button = Button(text='Save', size_hint=(1.0, 0.25))
        self.save_button.bind(on_press=self.save_image)

        self.text_grid.add_widget(MemeTextBox(self.on_top_changed))
        self.text_grid.add_widget(MemeTextBox(self.on_mid_changed))
        self.text_grid.add_widget(MemeTextBox(self.on_bot_changed))
        self.text_grid.add_widget(self.load_button)
        self.text_grid.add_widget(self.save_button)
        self.add_widget(self.text_grid)

        # Sadly can't load from a buffer and need to create files with current strategy. :(
        self.main_app.meme.render_no_text('preview.gif')
        self.main_app.meme.render_text_image('text.png')
        self.image_view = Image(
            source='preview.gif',
            anim_delay=0.05,
            pos_hint={
                'x': 0,
                'y': 0
            },
            allow_stretch=True,
            keep_ratio=True)
        self.image_text = Image(
            source='text.png',
            pos_hint={
                'x': 0,
                'y': 0
            },
            allow_stretch=True,
            keep_ratio=True)
        self.image_float = FloatLayout()
        self.image_float.add_widget(self.image_view)
        self.image_float.add_widget(self.image_text)
        self.add_widget(self.image_float)

        self.file_select_view = Popup(title='Select Image')
        self.file_chooser = FileChooserListView(rootpath='./')
        self.file_chooser.bind(on_submit=self.on_image_selected)
        self.file_select_view.add_widget(self.file_chooser)

    def on_top_changed(self, value, align):
        self.main_app.set_top(value)
        self.main_app.meme.set_top_align(align)
        self.main_app.meme.render_text_image('text.png')
        self.image_text.reload()

    def on_mid_changed(self, value, align):
        self.main_app.set_mid(value)
        self.main_app.meme.set_mid_align(align)
        self.main_app.meme.render_text_image('text.png')
        self.image_text.reload()

    def on_bot_changed(self, value, align):
        self.main_app.set_bot(value)
        self.main_app.meme.set_bot_align(align)
        self.main_app.meme.render_text_image('text.png')
        self.image_text.reload()

    def select_image(self, instance):
        self.file_select_view.open()

    def on_image_selected(self, instance, selection, touch):
        self.file_select_view.dismiss()
        self.main_app.meme.set_input(selection[0])
        self.main_app.meme.render_no_text('preview.gif')
        self.main_app.meme.render_text_image('text.png')
        self.image_text.reload()
        self.image_view.reload()

    def save_image(self, instance):
        self.main_app.meme.render('meme.gif')


class KvMemeApp(App):
    def build(self):
        self.meme = Meme('gifs/this_is_fine.gif')
        return MemeAppMainView(self)

    def set_top(self, value):
        self.meme.set_top(value)

    def set_mid(self, value):
        self.meme.set_mid(value)

    def set_bot(self, value):
        self.meme.set_bot(value)


class MemeApp(object):
    def __init__(self):
        self.root = Tk()
        self.root.title('Memez!!!!1!')
        self.mainframe = ttk.Frame(self.root, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.top = StringVar()
        self.top.trace('w', self.update_top)
        self.top_entry = ttk.Entry(self.mainframe, textvariable=self.top)
        self.top_entry.grid(column=0, row=0)

        self.mid = StringVar()
        self.mid.trace('w', self.update_mid)
        self.mid_entry = ttk.Entry(self.mainframe, textvariable=self.mid)
        self.mid_entry.grid(column=0, row=1)

        self.bot = StringVar()
        self.bot.trace('w', self.update_bot)
        self.bot_entry = ttk.Entry(self.mainframe, textvariable=self.bot)
        self.bot_entry.grid(column=0, row=2)

        self.filename = 'gifs/this_is_fine.gif'
        self.meme = Meme(self.filename)
        self.img = self.meme.render('test.gif')
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.button = ttk.Button(self.mainframe, image=self.tkimg)
        self.button.grid(column=1, row=0, rowspan=3, stick=(W, E))

        self.select_meme = ttk.Button(
            self.mainframe, text='Select Image', command=self.select_image)
        self.select_meme.grid(column=0, row=3)

        #self.button.pack()
        self.mainframe.pack()

    def run(self):
        self.root.mainloop()

    def update_top(self, var, align, *args):
        str = self.top.get()
        self.top.set(str)
        self.meme.set_top(str)
        self.meme.set_top_align(align)
        self.update_img()
        return True

    def update_mid(self, var, align, *args):
        str = self.mid.get()
        self.mid.set(str)
        self.meme.set_mid(str)
        self.meme.set_mid_align(align)
        self.update_img()
        return True

    def update_bot(self, var, align, *args):
        str = self.bot.get()
        self.bot.set(str)
        self.meme.set_bot(str)
        self.meme.set_bot_align(align)
        self.update_img()
        return True

    def select_image(self, *args):
        self.filename = tkFileDialog.askopenfilename(
            initialdir="/", title="Select file")
        self.meme.set_input(self.filename)

    def update_img(self):
        self.img = self.meme.render('temp.gif')
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.button['image'] = self.tkimg


def main():
    KvMemeApp().run()
    #MemeApp().run()


if __name__ == "__main__":
    main()
