import os
import sys
from tkinter import *
from tkinter.ttk import *
from script import search_and_download, geckodriver_path, check_imagemagick_dependency
import threading
from tkinter import messagebox
import pausing_stopping_variables

window = Tk()
window.title("G-Image-Scraper")


# window.rowconfigure([0, 1, 2, 3, 4, 5], weight=1, minsize=100)
# window.columnconfigure([0, 1, 2, 3, 4, 5], weight=1, minsize=100)

# ********** Functions & Classes **********

def start_seach():
    search_keyword = search_keyword_var.get()
    main_images = main_images_var.get()
    start_index = start_index_var.get()
    secondary_images = secondary_images_var.get()
    image_size = image_size_var.get()
    show_browser = show_browser_var.get()
    interact_manually = interact_manually_var.get()
    show_folder = show_folder_var.get()
    maintain_same_size_secondary = maintain_same_size_for_secondary_var.get()

    def search_and_open_folder():
        target_folder = search_and_download(search_keyword, geckodriver_path, main_images, start_index, image_size,
                                            secondary_images, interact_manually,maintain_same_size_secondary,  headless=show_browser)

        messagebox.showinfo("Information", "Finished the search")
        if show_folder:
            os.startfile(target_folder)
        pausing_stopping_variables.is_stopped = False
        pausing_stopping_variables.is_paused = False
        btn_pause['text'] = "Pause"

    if search_keyword and main_images >= 1:
        thread = threading.Thread(target=search_and_open_folder)
        thread.start()


class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(END, str)
        self.widget.see(END)

    def flush(self):
        pass


def stopping():
    pausing_stopping_variables.is_stopped = True


def toggle_pause_resume():
    if btn_pause['text'] == "Pause":
        btn_pause['text'] = "Resume"
        pausing_stopping_variables.is_paused = True
    else: # if btn_pause['text'] = "Resume"
        btn_pause['text'] = "Pause"
        pausing_stopping_variables.is_paused = False


# ********** Search Keyword **********

frm_search_keyword = Frame(master=window)
frm_search_keyword.pack(padx=5, pady=10)

lbl_search_keyword = Label(master=frm_search_keyword, text="Search Keyword:")
lbl_search_keyword.pack(side=LEFT)

search_keyword_var = StringVar()
ent_search_keyword = Entry(master=frm_search_keyword, width=50, textvariable=search_keyword_var)
ent_search_keyword.pack(side=RIGHT)

# ********** Primary/Secondary images and Index **********

frm_image_number_index = Frame(master=window)
frm_image_number_index.pack(padx=10, pady=10)

lbl_main_images = Label(master=frm_image_number_index, text="Main Images:")
lbl_main_images.pack(side=LEFT, padx=2)

main_images_var = IntVar(value=1)
spin_main_images = Spinbox(master=frm_image_number_index, from_=1, to=500, width=5, textvariable=main_images_var)
spin_main_images.pack(side=LEFT, padx=2)

lbl_start_index = Label(master=frm_image_number_index, text="Start Index:")
lbl_start_index.pack(side=LEFT, padx=2)

start_index_var = IntVar(value=0)
spin_start_index = Spinbox(master=frm_image_number_index, from_=1, to=500, width=5, textvariable=start_index_var)
spin_start_index.pack(side=LEFT, padx=2)

lbl_secondary_images = Label(master=frm_image_number_index, text="Secondary Images:")
lbl_secondary_images.pack(side=LEFT, padx=2)

secondary_images_var = IntVar(value=0)
spin_secondary_images = Spinbox(master=frm_image_number_index, from_=1, to=500, width=5,
                                textvariable=secondary_images_var)
spin_secondary_images.pack(side=LEFT, padx=2)

# ********** Image size / Show & Interact with browser **********

frm_size_browser_interact = Frame(master=window)
frm_size_browser_interact.pack(padx=10, pady=10)

lbl_image_size = Label(master=frm_size_browser_interact, text="Image Size:")
lbl_image_size.pack(side=LEFT, padx=2)

image_size_var = StringVar(value="Default")
cmb_image_size = Combobox(master=frm_size_browser_interact, values=["Default", "Large", "Medium", "Icon"], width=10,
                          textvariable=image_size_var)
cmb_image_size.pack(side=LEFT, padx=2)

show_browser_var = BooleanVar(value=True)
chk_show_browser = Checkbutton(master=frm_size_browser_interact, text="Show Browser", variable=show_browser_var,
                               onvalue=False, offvalue=True)
chk_show_browser.pack(side=LEFT, padx=2)

interact_manually_var = BooleanVar(value=False)
chk_interact_manually = Checkbutton(master=frm_size_browser_interact, text="Interact Manually",
                                    variable=interact_manually_var, onvalue=True, offvalue=False)
chk_interact_manually.pack(side=LEFT, padx=2)

maintain_same_size_for_secondary_var = BooleanVar(value=False)
chk_maintain_same_size_for_secondary = Checkbutton(master=frm_size_browser_interact, text="Maintain same size for secondary",
                                                   variable=maintain_same_size_for_secondary_var, onvalue=True, offvalue=False)
chk_maintain_same_size_for_secondary.pack(side=LEFT, padx=2)

def interact_manually_visible_when_browser_ticked(*args):
    if show_browser_var.get() == False:
        chk_interact_manually.configure(state=NORMAL)
    else:
        chk_interact_manually.configure(state=DISABLED)


show_browser_var.trace("w", interact_manually_visible_when_browser_ticked)
chk_interact_manually.configure(state=DISABLED)

# ********** Show folder **********

frm_show_folder = Frame(master=window)
frm_show_folder.pack(padx=10, pady=5)

show_folder_var = IntVar(value=0)
chk_show_folder = Checkbutton(master=frm_show_folder, text="Show folder with the downloaded images",
                              variable=show_folder_var, onvalue=1, offvalue=0)
chk_show_folder.pack(side=LEFT, padx=2)

# ********** Start/Pause/Stop buttons **********
frm_buttons = Frame(master=window)
frm_buttons.pack(padx=10, pady=5)

btn_start = Button(master=frm_buttons, text="Start Search", width=14, command=start_seach)
btn_start.pack(padx=10, side=LEFT)

btn_pause = Button(master=frm_buttons, text="Pause", width=10, command=toggle_pause_resume)
btn_pause.pack(padx=10, side=LEFT)

btn_stop = Button(master=frm_buttons, text="Stop", width=10, command=stopping)
btn_stop.pack(padx=10, side=LEFT)


# ********** Progress information **********

frm_progress_info = Frame(master=window)
frm_progress_info.pack(padx=10, pady=5)

lbl_progress_info = Label(master=frm_progress_info, text="Progress Information:")
lbl_progress_info.pack(padx=2, anchor=W)

txt_progress_info = Text(master=frm_progress_info, width=90, height=20)
txt_progress_info.pack(padx=2, pady=2)
sys.stdout = TextRedirector(txt_progress_info)

print("********************************************")
print("********** G-Image-Scraper *********")
print("********************************************")
check_imagemagick_dependency()
window.mainloop()
