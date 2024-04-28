from tkinter import Tk, Label, Button, Entry, StringVar, Text, END
from script import search_and_download, check_imagemagick_dependency, main_inputs, geckodriver_path
import sys

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(END, str)
        self.widget.see(END)

    def flush(self):
        pass

class ImageScraperApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Image Scraper")

        self.keyword_label = Label(self, text="Keyword")
        self.keyword_label.pack()
        self.keyword = StringVar()
        self.keyword_entry = Entry(self, textvariable=self.keyword)
        self.keyword_entry.pack()

        self.number_label = Label(self, text="Number of images")
        self.number_label.pack()
        self.number = StringVar()
        self.number_entry = Entry(self, textvariable=self.number)
        self.number_entry.pack()

        self.start_label = Label(self, text="Start number")
        self.start_label.pack()
        self.start = StringVar()
        self.start_entry = Entry(self, textvariable=self.start)
        self.start_entry.pack()

        self.size_label = Label(self, text="Image size")
        self.size_label.pack()
        self.size = StringVar()
        self.size_entry = Entry(self, textvariable=self.size)
        self.size_entry.pack()

        self.secondary_label = Label(self, text="Secondary images")
        self.secondary_label.pack()
        self.secondary = StringVar()
        self.secondary_entry = Entry(self, textvariable=self.secondary)
        self.secondary_entry.pack()

        self.headless_label = Label(self, text="Headless mode (y/n)")
        self.headless_label.pack()
        self.headless = StringVar()
        self.headless_entry = Entry(self, textvariable=self.headless)
        self.headless_entry.pack()

        self.search_button = Button(self, text="Search", command=self.search_images)
        self.search_button.pack()

        self.output_text = Text(self)
        self.output_text.pack()

        sys.stdout = TextRedirector(self.output_text)

    def search_images(self):
        keyword = self.keyword.get()
        number = int(self.number.get())
        start = int(self.start.get())
        size = self.size.get()
        secondary = int(self.secondary.get())
        headless = self.headless.get() == 'y'
        search_and_download(keyword, geckodriver_path, number, start, size, secondary, headless)
        self.output_text.insert(END, "Search completed.\n")


if __name__ == "__main__":
    app = ImageScraperApp()
    app.mainloop()

