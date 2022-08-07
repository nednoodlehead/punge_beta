import tkinter
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import tkinter as tk
import os
import sqlite3
from PIL import Image, ImageTk
import os.path
import urllib.request
import db
import time
import sqlalchemy.exc
from pytube import YouTube, Playlist
from sqlalchemy.orm import sessionmaker
import threading
import pydub
from pydub import AudioSegment
from pydub.playback import play
from pathlib import Path
import random
from pycaw.pycaw import AudioUtilities
import sys
from system_hotkey import SystemHotkey
import json
global_hotkey = SystemHotkey()
import data_clean as dc


# A kill()-able thread. Needed for the music. i forget source of this :(. will add later !
class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()
  method."""

    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
    trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True



# Initialized


class tkinter_main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1250x750+125+100")
        self.resizable(False, False)
        self.configure(bg="#272c34")
        self.title("Punge Testing")
        self.iconbitmap("./img/punge icon.ico")
        self.option_add('*tearOff', FALSE)
        # Data regarding active music being passed around to controller and currently_playing frame
        everyones_music.controller = self
        # TODO should take direct information from the song playing. something something, change the main_music_loop
        # TODO to take data directly from this self.music_obj. Sometimes when song is ending and shuffle is called, the
        # TODO song playing and the song punge says is playing mismatch. make it more uniform & standardized
        self.shared_data = {}
        self.music_obj = None
        self.viewed_playlist = 'Main'
        # Will set shared_data
        everyones_music.app_launch_setup_thr()
        # self.properclose required for the app to stop playing music on exit
        self.protocol("WM_DELETE_WINDOW", self.proper_close)
        # These bindings replace the regular alt-f4 to keep the json caching accurate. Without them, an alt-f4 would
        # Not behave properly
        self.bind("<Alt_L>F4", self.proper_close)
        self.bind("<Alt_R>F4", self.proper_close)
        # init images used for buttons!
        self.right_arrow_img = tk.PhotoImage(file="F:/Projects/Python Projects/punge/img/punge_right_new.png")
        self.left_arrow_img = tk.PhotoImage(file="F:/Projects/Python Projects/punge/img/punge_left_new.png")
        self.shuffle_on_img = tk.PhotoImage(file="F:/Adobe/Punge WIP/To use/shuffle_on_new.png")
        self.shuffle_off_img = tk.PhotoImage(file="F:/Adobe/Punge WIP/To use/shuffle_off_new.png")
        self.play_img = tk.PhotoImage(file="F:/Projects/Python Projects/punge/img/punge_play_new.png")
        self.pause_img = tk.PhotoImage(file="F:/Projects/Python Projects/punge/img/punge_pause_new.png")


        main_page_frame = tk.Frame(self)
        main_page_frame.pack(side="top", fill="both", expand=True)
        main_page_frame.grid_rowconfigure(0, weight=1)
        main_page_frame.grid_columnconfigure(0, weight=1)
        right_frame = ttk.Style()
        right_frame.configure('right.TFrame', background='#262626')
        bottom_frame_style = ttk.Style()
        bottom_frame_style.configure('bottom.TFrame', background='#1b1b1c')
        bottom_frame_button_style = ttk.Style()
        bottom_frame_scale = ttk.Style()
        bottom_frame_scale.configure('Horizontal.TScale', background='#1b1b1c')
        bottom_frame_button_style.configure('TButton', borderwidth=0, activeforeground="#1b1b1c",
                                activebackground="#1b1b1c", foreground="#1b1b1c", background="#1b1b1c")
        tk.Button(self, text='DEBUG !', command=everyones_music.debug).place(x=100, y=10)
        tk.Button(self, text='Playlist debug', command=everyones_music.list_debug).place(x=100, y=40)
        self.root_frame = ttk.Frame(self, style='right.TFrame', height=925, width=200)
        self.root_frame.place(x=1050, y=0)
        self.bottom_frame = ttk.Frame(self, style='bottom.TFrame', height=75, width=1250)
        self.bottom_frame.place(x=0, y=675)
        self.skip_forwards_img = Image.open("./img/punge_right_new.png")
        bottom_frame_text_style = ttk.Style()
        bottom_frame_text_style.configure('bottom.TLabel', background='#1b1b1c', foreground='#9e9e9e')
        self.bottom_frame_song = ttk.Label(self.bottom_frame, text="", style='bottom.TLabel')
        self.bottom_frame_album = ttk.Label(self.bottom_frame, text="", style='bottom.TLabel')
        self.bottom_frame_author = ttk.Label(self.bottom_frame, text="", style='bottom.TLabel')
        self.bottom_frame_skip_forwards = tk.Button(self.bottom_frame, image=self.right_arrow_img,
                                                     command=self.skip_forward_update_play, borderwidth=0,
                                                    activeforeground="#1b1b1c", activebackground="#1b1b1c",
                                                    foreground="#1b1b1c", background="#1b1b1c")
        self.bottom_frame_skip_backwards = tk.Button(self.bottom_frame, image=self.left_arrow_img,
                                                     command=self.skip_backwards_update_play, borderwidth=0,
                                                    activeforeground="#1b1b1c", activebackground="#1b1b1c",
                                                    foreground="#1b1b1c", background="#1b1b1c" )
        self.bottom_frame_shuffle = tk.Button(self.bottom_frame, text='',
                                                    command=self.shuffle_update_bundle, borderwidth=0,
                                                    activeforeground="#1b1b1c", activebackground="#1b1b1c",
                                                    foreground="#1b1b1c", background="#1b1b1c" )
        # all in bottom_frame_play get defined by self.update_play_pause, which handles all that logic
        self.bottom_frame_play = tk.Button(self.bottom_frame, borderwidth=0,
                                                    activeforeground="#1b1b1c", activebackground="#1b1b1c",
                                                    foreground="#1b1b1c", background="#1b1b1c")
        self.bottom_frame_volume = ttk.Scale(self.bottom_frame, from_=0.001, to=0.2, orient="horizontal",
                                             command=volume_slider_controller, style='Horizontal.TScale')
        # Which is called here, should default to text='play' * command=self.play_with_cooldown
        self.update_play_pause()
        self.update_shuffle()
        self.bottom_frame_song.place(x=110, y=10)
        self.bottom_frame_album.place(x=110, y=50)
        self.bottom_frame_author.place(x=110, y=30)
        self.bottom_frame_skip_forwards.place(x=525, y=15)
        self.bottom_frame_skip_backwards.place(x=335, y=15)
        self.bottom_frame_play.place(x=460, y=15)
        self.bottom_frame_shuffle.place(x=675, y=15)
        self.bottom_frame_volume.place(x=750, y=30)


        self.frames = {}
        for each_frame in (Main_page, Currently_playing, Settings, Download, mp4_downloader, active_playlist):
            frame = each_frame(main_page_frame, self)
            self.frames[each_frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Main_page)
        # Global hotkeys for ease of use :D. Should be adjustable and configurable
        # binds also need to be able to configure buttons to change states. Like text=shuffle or text=not shuffle.
        global_hotkey.register(['control', 'next'], callback=self.shuffle_update_bundle)
        global_hotkey.register(['control', 'right'], callback=self.skip_forward_update_play)
        global_hotkey.register(['control', 'left'], callback=self.skip_backwards_update_play)
        global_hotkey.register(['control', 'end'], callback=self.global_keybind_play)
        global_hotkey.register(['control', 'up'], callback=static_increment_bind)
        global_hotkey.register(['control', 'down'], callback=static_decrease_bind)
        self.query_all_playlists()
        self.playlist_menu_add = Menu(self.root_frame, tearoff=0)
        self.playlist_menu_add.add_command(label="New..", command=self.create_new_table)
        self.root_frame.bind("<Button-3>", self.playlist_menu_add_popup)
        self.playlist_menu_edit = Menu(self.root_frame, tearoff=0)
        self.playlist_menu_edit.add_command(label="Edit",
                                            command=lambda: self.playlist_edit(self.playlist_menu_edit.playlist))
        self.playlist_menu_edit.add_command(label="Delete",
                                            command=lambda: self.delete_playlist(self.playlist_menu_edit.playlist))
        # Used to prevent the race condition so every_mcs.app_launch_setup_thr doesn't run before this threading.event
        # is set
        everyones_music.flicker.set()

    def global_keybind_play(self, event=None):
        everyones_music.pause_play_toggle()
        self.update_play_pause()

    def shuffle_update_bundle(self, event=None):
        if everyones_music.shuffle is True:
            everyones_music.shuffle = False
            everyones_music.reassemble_list()
            self.bottom_frame_shuffle.configure(image=self.shuffle_off_img)
        else:
            everyones_music.shuffle = True
            everyones_music.scramble_playlist()
            self.bottom_frame_shuffle.configure(image=self.shuffle_on_img)

    # TODO perhaps update to contain the first if & elif into one if, and move the logic of 'is not playing yadda yadda'
    # TODO into the music class.
    def update_play_pause(self):
        if not everyones_music.thr.is_alive() and not everyones_music.pause_bool:
            self.bottom_frame_play.configure(image=self.play_img, command=self.play_with_cooldown)
        elif everyones_music.pause_bool is True:
            self.bottom_frame_play.configure(image=self.play_img, command=self.resume_pause_toggle)
        else:
            print(f'thr_isalive {everyones_music.thr.is_alive()} pausebool: {everyones_music.pause_bool}')
            self.bottom_frame_play.configure(image=self.pause_img, command=self.resume_pause_toggle)

    def skip_forward_update_play(self):
        everyones_music.skip_forwards()
        self.update_play_pause()

    def skip_backwards_update_play(self):
        everyones_music.skip_backwards()
        self.update_play_pause()

    def resume_pause_toggle(self):
        self.bottom_frame_play.configure(state='disabled')
        self.update_play_pause()
        everyones_music.pause_play_toggle()
        self.update_play_pause()
        self.bottom_frame_play.after(400, lambda: self.bottom_frame_play.configure(state='active'))

    def update_shuffle(self):
        if everyones_music.shuffle is True:
            print(f'update_shuf IS ON : {everyones_music.shuffle}')
            self.bottom_frame_shuffle.configure(image=self.shuffle_on_img)
        else:
            print(f'update_shuf IS OFF : {everyones_music.shuffle}')
            self.bottom_frame_shuffle.configure(image=self.shuffle_off_img)



    def send_update_labels(self):
        # Include little thumbnail eventually?
        # For some godforsaken reason, if this 'for' loop is removed, the labels fail to update. 'class has no bottom_
        # frame_song' headbutt. it like makes it double check. 'oh it is there, my bad'
        for _ in self.bottom_frame.winfo_children():
            pass
        self.bottom_frame_song.configure(text=self.music_obj.Title)
        self.bottom_frame_album.configure(text=self.music_obj.Album)
        self.bottom_frame_author.configure(text=self.music_obj.Author)

    def play_with_cooldown(self):
        everyones_music.play()
        self.bottom_frame_play.configure(state='disabled')
        self.bottom_frame_play.after(500, lambda: self.bottom_frame_play.configure(state='active'))
        self.update_play_pause()

    def playlist_edit(self, playlist):
        if playlist[0] == 'main':
            tk.messagebox.showerror(message="That operation cannot be preformed on main")
        else:
            self.playlist_menu_edit_popup(playlist)
            con = sqlite3.connect('./MAINPLAYLIST.sqlite')
            cur = con.cursor()


        self.refresh_playlists()
        self.query_all_playlists()

    def refresh_playlists(self):
        for item in self.root_frame.winfo_children():
            # We dont want to destroy the menu widgets. We lose functionalty after deleting playlist!
            if type(item) == tkinter.Button:
                item.destroy()


    def delete_playlist(self, playlist):
        if playlist[0] == 'main':
            tk.messagebox.showerror(message="That operation cannot be preformed on main")
        else:
            con = sqlite3.connect("./MAINPLAYLIST.sqlite")
            cur = con.cursor()
            cur.execute("SELECT Title from {}".format(playlist[0],))
            x = cur.fetchone()
            if x is None:
                cur.execute("DROP TABLE {}".format(playlist[0]))
                con.commit()
            else:
                final_chance = tk.messagebox.askokcancel(title="Are you sure?", message="Are you sure you want to delete? \n This playlist"
                                                                         "contains data")
                if final_chance is True:
                    cur.execute("DROP TABLE {}".format(playlist[0]))
                    con.commit()
        print(playlist[0])
        self.refresh_playlists()
        self.query_all_playlists()

    def playlist_menu_add_popup(self, event):
        try:
            self.playlist_menu_add.tk_popup(event.x_root, event.y_root)
        finally:
            self.playlist_menu_add.grab_release()

    def playlist_menu_edit_popup(self, playlistname):
        edit_rename = Toplevel(self)
        edit_rename.focus()
        edit_rename.geometry("250x250+1000+400")
        edit_rename.title("Rename playlist")
        edit_rename.configure(background="#272c34")
        new_playlist_name = StringVar()
        entry_playlist = ttk.Entry(edit_rename, textvariable=new_playlist_name)
        confirm_button = Button(edit_rename, text='Update', command=lambda:
                                        confirm_edit_destroy(new_playlist_name.get(), playlistname))
        confirm_button.place(y=100, x=75)
        entry_playlist.place(y=75, x=75)
        entry_playlist.insert(END, playlistname)
        entry_playlist.bind("<Return>", lambda e: confirm_edit_destroy(new_playlist_name.get(), playlistname))

        def confirm_edit_destroy(new, old):
            self.update_table_name(self.underscore_replace(new), old)
            edit_rename.destroy()
            edit_rename.update()


    def underscore_replace(self, to_replace):
        new_str = to_replace.replace(" ", "_")
        return new_str

    def update_table_name(self, new_playlist, old_playlist):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(f'new {new_playlist}, old: {old_playlist}')
        cur1.execute("ALTER TABLE {} RENAME to {}".format(old_playlist[0], new_playlist))
        con1.commit()
        self.refresh_playlists()
        self.query_all_playlists()

    def playlist_menu_popup(self, event, playlist_name):
        try:
            self.playlist_menu_edit.tk_popup(event.x_root, event.y_root)
            self.playlist_menu_edit.playlist = playlist_name
        finally:
            self.playlist_menu_edit.grab_release()

    def create_new_table(self):
        popup_rename_window = Toplevel(self)
        popup_rename_window.geometry("250x250+850+275")
        popup_rename_window.title("Rename :D")
        popup_rename_window.configure(background="#272c34")
        new_playlist_name = StringVar()
        playlist_entry = ttk.Entry(popup_rename_window, textvariable=new_playlist_name)
        playlist_entry.place(x=75, y=20)
        playlist_entry.focus()
        playlist_create = ttk.Button(popup_rename_window, text="Create!!", command=lambda: create_playlist_combine(playlist_entry.get()))
        playlist_create.place(x=75, y=45)

        def underscore_replace(to_replace):
            new_str = to_replace.replace(" ", "_")
            return new_str


        def create_playlist_combine(play_enter):
            table_backend(underscore_replace(play_enter))
            destroy_popup("none lol")

        def destroy_popup(event):
            popup_rename_window.destroy()
            popup_rename_window.update()



        def table_backend(playlist_entry_got):
            con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
            cur1 = con1.cursor()
            cur1.execute("CREATE TABLE IF NOT EXISTS " +playlist_entry_got+ " (Title TEXT, Author TEXT,Savelocation TEXT,SavelocationThumb TEXT,Album TEXT, Uniqueid TEXT NOT NULL PRIMARY KEY)")
            con1.commit()
            self.query_all_playlists()

    def query_all_playlists(self):
        default_y = 10
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        cur1.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = cur1.fetchall()
        for playlist_name in rows:
            newname = playlist_name[0].replace("_", " ")
            new_button = tk.Button(self.root_frame, wraplength=190, text=newname, background='#262626',
                                  foreground='#969595', borderwidth=0, activebackground="#262626",
                                  activeforeground='#969595', justify='left',
                                  command=lambda playlist_name=playlist_name: self.switch_to_playlist(playlist_name))
            playlist_option = Menu(new_button, tearoff=0)
            playlist_option.add_command(label='test', command=lambda: self.play_check(playlist_name))
            new_button.place(x=0, y=default_y)
            new_button.update()
            new_button.bind("<Button-3>", lambda e, playlist_name=playlist_name:
                                          self.playlist_menu_popup(e, playlist_name))
            default_y = default_y + new_button.winfo_height() + 10



    def play_check(self, active_playlist):
        print(active_playlist)

    def playlist_popup(self, event):
        try:
            self.playlist_menu_add.tk_popup(event.x_root, event.y_root)
        finally:
            self.playlist_menu_add.grab_release()


    def switch_to_playlist(self, playlist_in):
        self.viewed_playlist = playlist_in
        self.show_frame(active_playlist)


    def proper_close(self):
        try:
            everyones_music.stop()
            everyones_music.song_count -= 1
            everyones_music.set_shared_data()
            print(f'shared data AT END: {self.shared_data}')
            print(f'status of shuffle: {everyones_music.shuffle}')
            with open("./Cache/playlist.json", "w") as file:
                json.dump(self.shared_data, file)
        finally:
            sys.exit(10)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


class music_player:
    def __init__(self, controller=None):
        self.controller = controller
    # Song is used to hold the Pydub.Audiosegment used to be played.
    song = None
    # Start_time is the beginning of the loop, used in conjuction with now_time to detirmine when music is/isnt playing
    song_begin = 0
    pause_time = 0
    # Holds the threading object, also used to detirmine if a song is playing (more accurate than other methods)
    thr = threading.Thread()
    # Count refers to the index in current_playlist. it is incremented each time a song is finished
    song_count = 0
    # sleep timer is used to mirror the length of a song, so it can sleep for that long. playing doesn't halt the loop
    # It is also used to see how long needs to be rendered after resumung music. So it would be time played - sleeptimer
    sleeptimer = 0
    # Holds the current playlist. In either shuffled or normal mode
    current_playlist = []
    # holds integers. is used to cache when a user pauses the video. So it holds the time that has already been listened
    # to. So when paused, then resume, it begins are correct spot
    resume_list = []
    # Detirmines if shuffle is on or off. in progress
    shuffle = None
    # a flag used to stop the 'sleep'. normal time.sleep() can't be interupted (for pausing and whatnot). this can
    exited = threading.Event()
    # Used soley within the main_music_loop to detirmine whether the loop should reset the pause list. Because if this
    # Value is true, then it should, because it is a new song being played
    coming_from_loop = True
    # Is the music current paused? used mostly for skipping songs, to see if the music needs to be stopped()
    pause_bool = False
    # is the music playing. somehow differnt that pause_bool
    is_playing = False
    # Will hold the current music object being played. Will be used for shuffle recontruction (shuffle off -> on ->
    # comes back to same song), displaying current song.
    song_obj = None
    # Goal of this function is to run when app is launched, and 'restore' previous session playlist & song. this will
    # reduce the need for special causes around 'no song selected / no playlist selected'. and we will always be working
    # with valid objects at all times
    flicker = threading.Event()
    flicker.clear()
    # Flicker is used to prevent a race condition. When app_launch_startup begins, it opens on a new thread and tries
    # to set self.controller.send_update_labels, which can occur before the labels inside have been initialized. This
    # is apparent because when a time.sleep() is added to app_launch_setup, an error does not occur

    def app_launch_setup_thr(self):
        thr = threading.Thread(target=self.app_launch_setup)
        thr.start()

    def app_launch_setup(self):
        with open("./Cache/playlist.json") as file:
            x = json.load(file)
            print(x)
            # Sets the shared_data dict = to the json file
            self.controller.shared_data = x
            print(f'app_lauch sets controller.shared_data= {x}')
            print(f'self.shuffle: {x["shuffle"]} ')
            self.shuffle = x['shuffle']
            self.flicker.wait()
            # Queries the self.current_playlist, takes into account the status of self.shuffle
            self.query_list()
            songid = x['songid']
            # TODO FLICKER
            for count, entry in enumerate(self.current_playlist):
                if entry.Uniqueid == songid:
                    self.song_count = count
                    self.update_frame_labels(self.current_playlist[self.song_count])
                    self.song = AudioSegment.from_file(self.current_playlist[self.song_count].Savelocation)
                    print(f'song_con: {self.song_count} . song_obj: {self.controller.music_obj} song: {self.song}')
            print("app_launched!!!")



    def pause_play_toggle(self, extra=None):
        # If it is pausued:
        if self.pause_bool is True:
            self.resume_thread()
            self.pause_bool = False
        else:
            self.pause_bool = True
            self.stop()
    """
    Right now, an important part of what makes punge work ok is the class attirbutes start_time & now_time. These are
    essential for the music_player class to work properly.
    It mainly works off of having a time.sleep() (But its a different module or whatever, one that can be interupted) 
    and it will sleep for the entire song. The way it currently works, is that each time a pause occurs it will log the
    current time and time of last pause, then place it into list and yada yada. In short, it needs to be remade into
    a function that will go down while is_playing is true, and pause otherwise. This should fix the long-period-resume
    bug where resuming music after 20+minutes will cause a threading excepting and crash. it will also reduce load time,
    as it will be able to reproduce the audiosegment after the pause is called, because it will know the time to resume 
    at immediately after. Only downside is pausing and resuming repedatly will cause problems in terms of preformance
    """
    def kthread_check_thr(self):
        thr = threading.Thread(target=self.kthread_check)
        thr.start()



    def kthread_check(self):
        print('kthread called')
        k_count = []
        # Checks over every thread
        for thread in threading.enumerate():
            # Filters only Kthreads. KThreads play music only
            if type(thread) == KThread:
                # place each Kthread into the list
                k_count.append(thread)
            # Kill all Kthreads besides last. This allows the most recent thread began to 'win' and play
            for die_thread in k_count[:-1]:
                print(f'killing thread: {die_thread}')
                die_thread.kill()



    def thd(self):
        thr = threading.Thread(target=self.start_timer)
        thr.start()

    def start_timer(self):
        # Detirmine if the play is coming from the resume timer or natural loop. If it is coming from natural ->
        # clear self.resume_list() So the data for diferent songs doesn't persist
        ween = True
        while ween is True:
            print("Started timer")
            if self.coming_from_loop is True:
                print("Cleared list")
                self.resume_list.clear()
            self.start_time = time.time()
            time.sleep(10)



    def quit_out(self, signo=0, _frame=0):
        print("interupted by ", signo)
        self.exited.set()
        self.stop()
        self.exited.clear()

    def play(self):
        if self.thr.is_alive() is True:
            print("SONG IS ALREADY PLAYING. NOW STOPPING IT")
            everyones_music.stop()
            time.sleep(.5)
            #everyones_music.reset_class_defaults()
            print("THRD!")
            self.is_playing = True
            self.exited.clear()
            self.thr = KThread(target=self.testsong)
            self.song_begin = time.time()
            self.thr.start()
        else:
            print("THRD!")
            self.is_playing = True
            self.exited.clear()
            self.thr = KThread(target=self.testsong)
            self.song_begin = time.time()
            self.thr.start()
        self.kthread_check_thr()



    def resume_thread(self):
        self.is_playing = True
        self.thr = KThread(target=self.resume)
        self.thr.start()
        self.song_begin = time.time()
        print(f'Should be true 1 : {self.thr.is_alive()}')
        print(f'Should be true 2 : {self.thr.is_alive()}')

    def event_clear(self):
        time.sleep(1)
        self.exited.clear()


    def check(self):
        print(f'status thread: {self.thr.is_alive()}')


    def testsong(self, called_with=None):
        print("TESTSONG CALLED")
        """
        THis portion is needed as a pre-requisite to the main_music_loop() because when resume calls, it needs to pass
        in the new self.song. And when playing for the first time, It needs to define the varibale. So with this
        function, we define both of those (New definitions ((loop based)) are created after the self.playback is called)
        """
        if called_with == None:
            self.set_shared_data()
            self.controller.music_obj = self.current_playlist[self.song_count]
            self.controller.send_update_labels()
            self.song = AudioSegment.from_file(self.controller.music_obj.Savelocation)
            try:
                self.main_music_loop()
            except RuntimeError:
                pass # Used to ignore warning on app close. Not 100% sure why this calls like this though...
        else:
            self.main_music_loop()


    def main_music_loop(self):
        self.print_debug("main_music_loop")
        if self.coming_from_loop is True:
            self.resume_list.clear()
        while not self.exited.is_set():
            # Reset True status so if resume isn't called (sets to false) the resume_list is cleared
            self.coming_from_loop = True
            try:
                # tries to mimic the length of the song for pausing / resuming purposes
                self.song_begin = time.time()
                self.playback = pydub.playback._play_with_simpleaudio(self.song)
                # Adjusting the class variables for next time the loop runs
                self.sleeptimer = self.song.duration_seconds
                # tells the bottombar to update to new music_obj
                self.controller.send_update_labels()
                self.set_shared_data()
                # Defines next song in rotation (based on incrementing number in list index)
                self.song_count = self.song_count + 1
                # Begins class variable timer. Uses so resume() knows where to pick up from
                # Essentially time.sleep() but can be interupted by flags ( self.exited.is_set() )
                print(f'current song: {self.current_playlist[self.song_count - 1].Title} sngcount: {self.song_count-1}')
                self.exited.wait(self.sleeptimer)
                # Creates the audiosegment from the new song
                self.controller.music_obj = self.current_playlist[self.song_count]
                self.song = AudioSegment.from_file(self.controller.music_obj.Savelocation)
                # Might not be needed cause its done above... unsure though
                #self.controller.send_update_labels()
                print(f"main_music has turned song_obj into: {self.controller.music_obj}")
                # Makes the resume will make this false if called, else: it'll clear the list each time
                self.coming_from_loop = True
                self.kthread_check_thr()
            except IndexError:
                # Catches when the final song is played and dives back in. Perhaps a reshuffle at this point?
                print("index error raied in main loop")
                # Loops back to beginning of playlist if the final song is played
                self.song_count = 0
                # Loads the first song
                self.controller.music_obj = self.current_playlist[self.song_count]
                self.song = AudioSegment.from_file(self.controller.music_obj.Savelocation)
                self.update_frame_labels(self.current_playlist[self.song_count])
                self.set_shared_data()
                # Continues loop -> to first song
                continue




    def list_debug(self):
        print(f"PLAYLIST: {self.controller.shared_data['playlist']}")
        print(f'list_debug cursong: {self.controller.music_obj}')
        for item in self.current_playlist[self.song_count - 1:self.song_count + 5]:
            print(item.Title)
        print("\n \n")

    def debug(self):
        print("###THR DEBUG###")
        for th in threading.enumerate():
            print(f'thread: {th}')
            print(f'type: {type(th)}')
        print('kthreads only:')
        for threa in threading.enumerate():
            if type(threa) == KThread:
                print(f'kthrad locatied::: {threa}')
        print("***JSON DEBUG***")
        print(self.controller.shared_data)
        print("-----DEBUG----")

        print(f"self.song: {self.song}")
        print(f"self.pause_time: {self.pause_time}")
        print(f"self.thr: {self.thr}")
        print(f"self.song_count: {self.song_count}")
        print(f"self.sleeptimer: {self.sleeptimer}")
        print(f"self.current_playlist: {self.current_playlist}")
        print('----')
        print(f'previous song: {self.current_playlist[self.song_count - 1]}')
        print(f'current song: {self.current_playlist[self.song_count]}')
        print(f'next song: {self.current_playlist[self.song_count + 1]}')
        print('----')
        print(f"self.resume_list: {self.resume_list}")
        print(f"self.shuffle: {self.shuffle}")
        print(f"self.exited: {self.exited}")
        print(f"self.coming_from_loop: {self.coming_from_loop}")
        print(f"self.pause_bool: {self.pause_bool}")
        print(f"self.: {self.controller.music_obj}")
        print(f'is thread active?: {self.thr.is_alive()}')
        print(f'is playing: {self.is_playing}')
        print("-----DEBUG----")

    def update_frame_labels(self, song_object):
        self.controller.music_obj = song_object
        self.controller.send_update_labels()

    def reset_class_defaults(self):
        print('reset defaults called')
        #self.stop()
        self.song = None
        self.start_time = 0
        self.thr = None
        #self.song_count = 0
        self.sleeptimer = 0
        # self.current_playlist = []
        self.resume_list = []
        # Shuffle not included rn
        self.exited = threading.Event()
        self.coming_from_loop = True
        self.pause_bool = False
        self.is_playing = False

    def set_shared_data(self):
        print(f'song_obj: {self.controller.music_obj}')
        #print(f'song_obj[5]: {self.controller.music_obj.Uniqueid}')
        self.controller.shared_data['songid'] = self.current_playlist[self.song_count].Uniqueid
        self.controller.shared_data['shuffle'] = self.shuffle

    def stop(self):
        print(f'obj: {self.controller.music_obj}')
        self.is_playing = False
        self.pause_time = time.time() - self.song_begin
        self.pause_time *= 1000
        self.exited.set()
        self.playback.stop()
        # Needed to reset the exited timer. One to flick it, one to reset to neutral
        self.exited.set()
        #self.print_debug("stop")

    def skip_forwards(self, option=None):
        self.coming_from_loop = False
        if self.pause_bool is False:
            # Kills the self.exited.wait() timer
            self.exited.set()
            # Kills the audiosegment playing
            try:
                # Try loop so on begin it doesn't cry
                self.stop()
            except AttributeError:
                self.song_count += 1
                self.play()
            finally:
                # Resets the status of self.exited.clear() it will be ready to play again
                self.exited.clear()
                # No song_count increment needed because the loop by default, increments song_count
                self.resume_list.clear()
                print(f"pause_bool rn: {self.pause_bool}")
        else:
            print("skipforwards debug:")
            self.print_debug("skip_forwards")
            self.exited.clear()
            self.resume_list.clear()
            self.play()
            self.pause_bool = False



    def print_debug(self, call_method):
        print(f'called by:  {call_method}')
        print(f'self.thr: {self.thr}')
        print(f'self.exited.isSet bool: {self.exited.is_set()}')
        print(f'self.pause_bool: {self.pause_bool}')
        print(f'self.coming_from_loop: {self.coming_from_loop}')
        print('\n \n')


    def skip_backwards(self, option=None):
        self.coming_from_loop = False
        if self.song_count == 1:
            print('can\'t be going back like dat!')
        else:
            if self.pause_bool is False:
                self.exited.set()
                self.song_count = self.song_count - 2
                try:
                    self.stop()
                except AttributeError:
                    self.play()
                self.exited.clear()
                self.resume_list.clear()
            else:
                self.song_count = self.song_count - 2
                self.exited.clear()
                self.resume_list.clear()
                self.play()
                self.pause_bool = False


    def add_times(self):
        to_return = 0
        for item in self.resume_list:
            to_return += item
        return to_return

    # TODO a fix for the spam-clicking of play/pause, is when resume here is called, it sets a .controller flag so that
    # TODO it cannot be re-called until resume has finished executing
    def resume(self):
        print("##RESUME##")
        self.exited.clear()
        print(f'index at beginning of resume() {self.song_count}')
        # Makes it replay the song that was just stopped (offsetting the +1 form the original function)
        # Current time in miliseconds (metric pydub operates in)
        # Defines class variable as only a portion of a song
        self.resume_list.append(self.pause_time)
        # -1 needed to counteract the +1 at end of main_loop
        self.song_count -= 1
        new_time = 0
        self.controller.music_obj = self.current_playlist[self.song_count]
        self.song = AudioSegment.from_file(self.controller.music_obj.Savelocation)
        for true_time in self.resume_list:
            new_time += true_time
        print(f'new_time (should be in ms) = {new_time}')
        self.song = self.song[new_time:]
        print(f'self.song len() : {self.song.duration_seconds}')
        print(f'main_part (resume): {type(self.playback)}')
        self.coming_from_loop = False
        self.testsong("yella")
        print(f'index at end of resume() {self.song_count}')


    def query_list(self):
        new_list = self.controller.shared_data['playlist'].replace(" ", "_")
        big_ol_list = []
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        cur1.execute("SELECT Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid FROM {}".format(new_list))
        rows = cur1.fetchall()
        for each in rows:
            imported_music = import_music(*each)
            big_ol_list.append(imported_music)
        print(f'big ol list: {big_ol_list[0:3]}')
        print(f'self.shuffle: {self.shuffle}')
        if self.shuffle is True:
            random.shuffle(big_ol_list)
        self.current_playlist = big_ol_list



    def scramble_playlist(self):
        songid = self.controller.music_obj.Uniqueid
        # When shuffling, will set song_count = music_obj's current spot in the new list. So if song1 is at 124. Shuffle
        # Now that song is at position 514. It will set the song_count = 514. So shuffle -> skip for -> skip back
        # Puts user on correct song
        random.shuffle(self.current_playlist)
        for count, entry in enumerate(self.current_playlist):
            if entry.Uniqueid == songid:
                # not entirely sure why i need +1. I added it and it works as expected..
                everyones_music.song_count = count + 1



    def reassemble_list(self):
        # Grabs the id of current song to begin at.
        cur_id = self.controller.music_obj.Title
        print(f'title we\'re taking: {cur_id}')
        # turns self.current_playlist into an unscrambled version
        self.query_list()
        print(f"Should be current song: {self.current_playlist[self.song_count].Title}")
        # Iterate over each entry of said playlist
        for entry in self.current_playlist:
            # Find where the current song sits in the unqueried list, set song_count to that number
            if entry.Title == cur_id:
                print(f"current song to grab is: {entry.Title}")
                x = self.current_playlist.index(entry)
                print(f'x: (value of {cur_id}: {x}')
                if everyones_music.pause_bool is True: #new???
                    self.song_count = x
                else:
                    self.song_count = x + 1  # bruh. all i got to say
                # +1 required because when index is got, it will get the index of the active, playing song. we want it
                # to play the next song up.
                print(f'end of reasemble  song_count {self.current_playlist[self.song_count].Title}')



everyones_music = music_player()




everyones_music.controller = tkinter_main

class Main_page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        #Buttons
        button_main = Button(self, text="Main page", state=DISABLED)
        button_download = Button(self, text="Download", command=lambda: controller.show_frame(Download))
        button_settings = Button(self, text="Settings", command=lambda: controller.show_frame(Settings))
        button_current = Button(self, text="Currently playing", command=lambda: controller.show_frame(Currently_playing))
        button_mp4 = Button(self, text="Video downloader", command=lambda: controller.show_frame(mp4_downloader))
        button_main.place(x=0, y=125)
        button_current.place(x=0, y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0, y=200)
        button_mp4.place(x=0, y=225)





class Currently_playing(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        Label(self, text="THIS IS Currently playing tab").pack()
        button_main = Button(self, text="Main page", command=lambda: controller.show_frame(Main_page))
        button_download = Button(self, text="Download", command=lambda: controller.show_frame(Download))
        button_settings = Button(self, text="Settings", command=lambda: controller.show_frame(Settings))
        button_current = Button(self, text="Currently playing", state=DISABLED)
        button_mp4 = Button(self, text="Video downloader", command=lambda: controller.show_frame(mp4_downloader))
        button_playlist = Button(self, text="Currently playlist", command=lambda: controller.show_frame(active_playlist))
        button_main.place(x=0, y=125)
        button_current.place(x=0, y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0, y=200)
        button_mp4.place(x=0, y=225)
        button_playlist.place(x=0, y=250)


        #I hate images in tkinter
        #    path1 = Image.open("F:/Files at random/MUSICAL/thumbnails/Death Grips - HackeruoZgZT4DGSY.jpg")
        #    opened_thumb = ImageTk.PhotoImage(path1)
        #    mei = Label(self, image=opened_thumb)
        #    mei.place(x=200, y=200)

        play_button = ttk.Button(self, text="Play", command=everyones_music.thd) #added args of selected playlist
        play_button.place(relx=.5, rely=.8)

        slider = ttk.Scale(self, from_=0.01, to=0.2, orient="horizontal", command=volume_slider_controller)
        slider.place(rely=.5, relx=.5)

        self.resume_button = ttk.Button(self, text="TESTING BUTTON", command=self.resume_pause_toggle)
        self.resume_button.place(relx=.5, rely=.75)

#        self.shuffle_button = ttk.Button(self, text="Shuffle (off)", command=everyones_music.update_playlist)
#        self.shuffle_button.place(x=250, y=400)

        mute_button = ttk.Button(self, text="mute", command=volume_mute)
        mute_button.place(rely=.5, relx=.65)

        skip_forwards = ttk.Button(self, text="Skip LOL", command=everyones_music.skip_forwards)
        skip_forwards.place(rely=.3, relx=.5)

        skip_backwards = ttk.Button(self, text="Skip back", command=everyones_music.skip_backwards)
        skip_backwards.place(rely=.85, relx=.25)
        # self.shuffle_toggle()  # Called so it defaults properly

    def resume_pause_toggle(self):
        self.play_pause_update()
        everyones_music.pause_play_toggle()
        self.play_pause_update()

    def play_update(self):
        everyones_music.query_list()
        print("CALLED BY play_update")
        everyones_music.play()

    def play_pause_update(self):
        if not everyones_music.thr.is_alive() and not everyones_music.pause_bool:
            self.resume_button.configure(text="Play", command=everyones_music.play)
        elif everyones_music.pause_bool is True:
            self.resume_button.configure(text="Resume", command=self.resume_pause_toggle)
        else:
            print(f'thr_isalive {everyones_music.thr.is_alive()} pausebool: {everyones_music.pause_bool}')
            self.resume_button.configure(text="Stop", command=self.resume_pause_toggle)


    def shuffle_button_refresh(self):
        # This controls the entire shuffle system. everytime this button is clicked it will either scramble playlist
        # or find the index of the song relative to the unshuffled playlist and start from there.
        print(f'shuffle: {everyones_music.shuffle}')
        if everyones_music.shuffle is True:
            print("playlist scrambled!")
            self.shuffle_button.configure(text="Shuffle (turn off)")
        else:
            print("list reassemabled!")
            self.shuffle_button.configure(text="shuffle (Turn on)")



class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        Label(self, text="THIS IS Settings location :D").pack()
        button_main = Button(self, text="Main page", command=lambda: controller.show_frame(Main_page))
        button_current = Button(self, text="Currently playing", command=lambda: controller.show_frame(Currently_playing))
        button_download = Button(self, text="Download", command=lambda: controller.show_frame(Download))
        button_settings = Button(self, text="Settings", state=DISABLED)
        button_mp4 = Button(self, text="Video downloader", command=lambda: controller.show_frame(mp4_downloader))
        button_main.place(x=0, y=125)
        button_current.place(x=0,y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0,y=200)
        button_mp4.place(x=0, y=225)
        self.json_button = tk.Button(self, text='add to json', command=self.add_entry)
        self.json_button.place(x=500, y=200)
        self.path = "./Cache/downloadlocation.json"
        self.new_path = tk.StringVar()
        self.json_entry = tk.Entry(self, textvariable=self.new_path)
        self.json_entry.place(x=500, y=225)
        self.view_json = tk.Button(self, text='view json', command=self.read_entries)
        self.view_json.place(x=500, y=250)
        self.curJson = self.read_entries()
        self.delete_combobox = ttk.Combobox(self, width=25, values=self.curJson)
        self.delete_combobox.set(self.curJson[0])
        self.delete_combobox.place(x=700, y=225)
        self.delete_button = ttk.Button(self, text='Delete!', command=self.delete_from_combobox)
        self.delete_button.place(x=700, y=250)
        self.clean_button = ttk.Button(self, text='Clean Folders', command=self.clean_confirm)
        self.clean_button.place(x=750, y=15)

    def clean_confirm(self):
        is_sure = tk.messagebox.askokcancel('Are you sure?', "This will delete all files in your Punge download folder"
                                                             "that isn't listed in the Database (MAINPLAYLIST.sqlite)")
        if is_sure is True:
            dc.delete_all(dc.in_dir_not_db()[0], dc.in_dir_not_db()[1])


    def read_entries(self):
        with open(self.path, 'r') as file:
            x = json.load(file)
            print(x)
            self.curJson = x
            return x


    def add_entry(self):
        add_to_json = self.json_entry.get()
        if os.path.exists(add_to_json) is False:
            print('path no exist!!')
            tk.messagebox.showerror('Error', 'You Need to enter a valid path!')
        else:
            x = add_to_json.replace('\\', '/')
            print('path do exist')
            old_entries = self.read_entries()
            with open(self.path, 'w') as file:
                old_entries.append(x)
                json.dump(old_entries, file)
            self.json_entry.delete(0, 'end')
            self.combo_update()

    def combo_update(self):
        self.delete_combobox.configure(values=self.curJson)
        self.delete_combobox.set(self.curJson[0])


    def delete_from_combobox(self):
        delete = self.delete_combobox.get()
        with open(self.path, 'r') as file:
            myjson = json.load(file)
            print(myjson)
            for entry in myjson:
                print(f'entry!')
                if entry == delete:
                    myjson.remove(entry)
            print(f'newjson!!: {myjson}')
            self.curJson = myjson
            self.combo_update()
        with open(self.path, 'w') as file_2:
            json.dump(myjson, file_2)



class Download(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        Label(self, text="THis is where downloading will occur").pack()
        Label(self, text="Will include a search area aswell. Including clipboard mode").pack() #TODO Search functionality
        button_main = Button(self, text="Main page", command=lambda: controller.show_frame(Main_page))
        button_current = Button(self, text="Currently playing", command=lambda: controller.show_frame(Currently_playing))
        button_download = Button(self, text="Download", state=DISABLED)
        button_settings = Button(self, text="Settings", command=lambda: controller.show_frame(Settings))
        button_mp4 = Button(self, text="Video downloader", command=lambda: controller.show_frame(mp4_downloader))
        button_main.place(x=0, y=125)
        button_current.place(x=0, y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0, y=200)
        button_mp4.place(x=0, y=225)

        # -----Listism-----#
        elite_fileloc = "F:/Punge Downloads/Downloads/"  # These will be detirmined by user eventualy
        elite_fileloc_thumbnail = "F:/Punge Downloads/thumbnails/"
        auto_album_recognize = "Provided"
        forbidden_character = "<>:\"/\|?*"
        ytlink_strvar = tk.StringVar()
        # -----Functions-N-Stuff-----#
        #ytlink_inputbox = Entry(self, bg=)
        def ytlink_box_get_thread(*event):
            thread1 = threading.Thread(target=ytlink_box_get, args=("*event"))
            thread1.start()
        def ytlink_box_get(*event):
            ytlink = ytlink_strvar.get()
            download_differentiate(ytlink)
            ytlink_entry.delete(0, 'end')
        ytlink_entry = ttk.Entry(self, textvariable=ytlink_strvar, width=30)
        download_button = ttk.Button(self, text="Download!", command=ytlink_box_get_thread)
        ytlink_entry.pack()
        download_button.pack()
        ytlink_entry.bind("<Return>", ytlink_box_get_thread)



        def download_single(ytlink):
            video_main = YouTube(ytlink)
            video1 = video_main.streams.get_audio_only()
            download_path_ext = file_extension_change_mp3(video_main.author, video_main.title, video_main.video_id)
            print("dwnload single1: " + download_path_ext)
            download_path_ext = download_path_ext.strip()
            print("dwnload single2: " + download_path_ext)
            if os.path.exists(download_path_ext) is True:
                print("File already downloaded. Try something new.")
            else:
                bruh = video1.download(output_path=elite_fileloc)
                os.rename(bruh, download_path_ext)
                urllib.request.urlretrieve(video_main.thumbnail_url,
                                           file_extension_change_jpg(video_main.author, video_main.title, video_main.video_id))
                add_to_db(video_main.author, video_main.title, video_main.video_id, video_main.description)

        def download_playlist(ytlink):  # try except and skip downloaded songs
            video1 = Playlist(ytlink)
            for video_main in video1.videos:
                downloadname = playlist_mp3_fix(video_main.author, video_main.title, video_main.video_id)
                try:
                    video_sep2 = video_main.streams.get_audio_only()
                except:
                    # Needed for anti-private / age restircted videos
                    continue
                print('I will now continue ! (implies not private or restricted)')
                if os.path.exists(downloadname) is True:
                    print("File already downloaded(playlist). Try something new.")
                else:
                    bruh = video_sep2.download(output_path=elite_fileloc)
                    try:
                        os.rename(bruh, downloadname) #changed to include video_id for times when the title and author are identical
                    except FileExistsError:
                        print("ALready added, going on...") #TODO when downloading vid that exists, creates mp4 version. it should delete it instead. problem #354
                        urllib.request.urlretrieve(video_main.thumbnail_url,
                                                   file_extension_change_jpg(video_main.author, video_main.title, video_main.video_id))
                        add_to_db(video_main.author, video_main.title,
                                  video_main.video_id, video_main.description)
                        #Could be a function but eh
                    urllib.request.urlretrieve(video_main.thumbnail_url, #Most effects name like Jay-Z. Where jay = title and z = artist. try to make "jay - z.mp3"
                                               file_extension_change_jpg(video_main.author, video_main.title, video_main.video_id))
                    add_to_db(video_main.author, video_main.title,
                              video_main.video_id, video_main.description)

        def download_differentiate(ytlink):
            if "list=" in ytlink:
                download_playlist(ytlink)
            else:
                download_single(ytlink)

        def playlist_mp3_fix(vid_auth, vid_titl, vid_id):
            pt1 = (difference_author_title(vid_auth, vid_titl)[1] + " - " +
                   difference_author_title(vid_auth, vid_titl)[0])
            pt1_fixed1 = character_replacer(pt1)
            pt1_fixed2 = elite_fileloc + pt1_fixed1 + vid_id + ".mp3"
            return pt1_fixed2

        def add_to_db(vid_auth, vid_titl, vid_id, vid_desc):
            part1_db = difference_author_title(vid_auth, vid_titl)[0],
            #Fix for part1_db being a tuple for whatever reason
            part1_fixed = ''.join(part1_db)
            print(f'PART THAT MESSES UP: {part1_db}')
            part2_db = difference_author_title(vid_auth, vid_titl)[1]
            print(f'should look normal: {part2_db}')
            part3_db = file_extension_change_mp3(vid_auth, vid_titl, vid_id)
            part4_db = file_extension_change_jpg(vid_auth, vid_titl, vid_id)
            part5_db = album_check(vid_desc)
            part6_db = vid_id

            class_object = db.import_info123(part1_fixed, part2_db, part3_db, part4_db, part5_db, part6_db)
            try:
                Session = sessionmaker(bind=db.engine)
                session = Session()
                session.add(class_object)
                session.commit()
            except sqlalchemy.exc.IntegrityError:
                Session = sessionmaker(bind=db.engine) #could be optimized with function ?
                session = Session()
                session.rollback()
                print("Inserted already")

        def character_replacer(phrase):
            mainpart_fixed = ''
            for letter in phrase:
                if letter in forbidden_character:
                    mainpart_fixed = mainpart_fixed + ''
                else:
                    mainpart_fixed = mainpart_fixed + letter
            return mainpart_fixed

        def character_replacer_vevo(phrase):
            if 'VEVO' in phrase:
                first_letter_check = True
                mainpart_fixed2 = phrase[:-4]
                mainpart_fixed = ''
                for letter in mainpart_fixed2:
                    if letter.isupper() is True and first_letter_check is False:
                        mainpart_fixed = mainpart_fixed + " " + letter
                    else:
                        mainpart_fixed = mainpart_fixed + letter
                        first_letter_check = False
                return mainpart_fixed
            else:
                mainpart_fixed = phrase
                return mainpart_fixed

        def file_extension_change_mp3(vid_auth, vid_titl, vid_id):
            change_mp3_author = difference_author_title(vid_auth, vid_titl)[1]
            change_mp3_title = difference_author_title(vid_auth, vid_titl)[0]
            change_mp3_author_fixed = character_replacer_vevo(change_mp3_author)
            change_mp3_title_fixed = character_replacer(change_mp3_title)
            mainpart = change_mp3_author_fixed + " - " + change_mp3_title_fixed
            export_file_mp3 = elite_fileloc + mainpart + vid_id + ".mp3"
            print(export_file_mp3)
            return export_file_mp3

        def file_extension_change_jpg(vid_auth, vid_titl, vid_id):
            mainpart = (difference_author_title(vid_auth, vid_titl)[1] + " - " +
                        difference_author_title(vid_auth, vid_titl)[0])
            mainpart_fixed = character_replacer(mainpart)
            export_file_jpg = elite_fileloc_thumbnail + mainpart_fixed + vid_id + ".jpg"
            return export_file_jpg


        def author_title_decide(vid_auth, vid_titl):

            author_fixed = vid_auth[:-8]  # Sorts out > name - topic [bugged one]
            title_fixed = vid_titl
            return title_fixed.strip(), author_fixed.strip()

        def title_author_split(vid_auth, vid_titl):
            title_fixed = vid_titl.split("-")[1]  # Sorts out title based name / title [not bugged]
            author_fixed = vid_titl.split("-")[0]
            return title_fixed.strip(), author_fixed.strip()

        def title_neither(vid_auth, vid_titl):
            title_fixed = vid_titl  # sorts out author = artists and YTTitle = SongTitle
            author_fixed = vid_auth
            return title_fixed.strip(), author_fixed.strip()

        def difference_author_title(vid_auth, vid_titl):

            if "Topic" in vid_auth:
                return author_title_decide(vid_auth, vid_titl)
            elif "-" in vid_titl:
                return title_author_split(vid_auth, vid_titl)
            else:
                return title_neither(vid_auth, vid_titl)


        def album_check(description): #redefine to take information straight from video_main.desc
            if auto_album_recognize in description:
                description = description.split("\n")
                imported_album = description[4]
            else:
                imported_album = "Single"
            return imported_album
        def funny_check(self, event):
            print("Ive tried my best")
        #self.yt_link_entry.bind("<Return>", self.bind(funny_check))

class mp4_downloader(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        self.controller = controller
        button_main = Button(self, text="Main page", command=lambda: controller.show_frame(Main_page))
        button_current = Button(self, text="Currently playing", command=lambda: controller.show_frame(Currently_playing))
        button_download = Button(self, text="Download", command=lambda: controller.show_frame(Download))
        button_settings = Button(self, text="Settings", command=lambda: controller.show_frame(Settings))
        button_mp4 = Button(self, text="Video downloader", state=DISABLED)
        button_main.place(x=0, y=125)
        button_current.place(x=0,y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0,y=200)
        button_mp4.place(x=0, y=225)
        self.yt_link_stringvar = StringVar()
        self.YOUTUBEBOX = ttk.Entry(self, textvariable=self.yt_link_stringvar)
        self.YOUTUBEBOX.place(rely=.40, relx=.5, anchor=CENTER, width=250)
        self.YOUTUBEBOX.bind("<Return>", self.yt_link_get_thread)
        self.download_button = ttk.Button(self, text="Get!", command=self.yt_link_get_thread)
        self.download_button.place(rely=.45, relx=.5, anchor=CENTER)
        self.mp3_vs_mp4_list = [".MP4", ".MP3", ".MP4"]
        self.mp3_vs_mp4 = StringVar()
        self.mp4_mp3_differ_box = ttk.OptionMenu(self, self.mp3_vs_mp4, *self.mp3_vs_mp4_list)
        self.mp4_mp3_differ_box.place(x=770, y=287)
        with open("./Cache/downloadlocation.json") as file:
            self.desire_path_values = json.load(file)
        self.desire_path = ttk.Combobox(self, width=50, values=self.desire_path_values)
        self.desire_path.set(self.desire_path_values[0])  # Should be settable by user ?
        self.desire_path.place(relx=.5, rely=.5, anchor=CENTER)
        self.x_button = ttk.Button(self, text='X', command=self.clear_youtubebox, width=2)
        self.x_button.place(x=470, y=287)
        self.bind("<<ShowFrame>>", self.on_page_swap)




    def download_mp3_playlist(self, youtube_link, pathism):
        video1 = Playlist(youtube_link)
        for video_main in video1.videos:
            video_sep2 = video_main.streams.get_audio_only()
            bruh_change = video_sep2.download(output_path=pathism)
            pre, ext = os.path.splitext(bruh_change)
            os.rename(bruh_change, pre + ".mp3")

    def download_mp3_single(self, youtube_link, pathism):
        video1 = YouTube(youtube_link)
        video_main = video1.streams.get_audio_only()
        print(video_main.title)
        bruh_change = video_main.download(output_path=pathism)
        pre, ext = os.path.splitext(bruh_change)
        os.rename(bruh_change, pre + ".mp3")

    def download_mp4_playlist(self, youtube_link, pathism):
        video1 = Playlist(youtube_link)
        for video_main in video1.videos:
            video_sep2 = video_main.streams.get_highest_resolution()
            video_sep2.download(output_path=pathism)

    def download_mp4_single(self, youtube_link, pathism):
        video1 = YouTube(youtube_link)
        vid_download = video1.streams.get_highest_resolution()
        print(vid_download.title)
        vid_download.download(output_path=pathism)




    def download_mp3_differ(self):
        pathism = self.desire_path.get()
        if os.path.exists(pathism) is False:
            print("Choose a proper path lil bruh")
        else:
            youtube_link = self.yt_link_stringvar.get()
            if "list=" in youtube_link:
                self.download_mp3_playlist(youtube_link, pathism)
            else:
                self.download_mp3_single(youtube_link, pathism)

    def download_mp4_differ(self):
        pathism = self.desire_path.get()
        youtube_link = self.yt_link_stringvar.get()
        if "list=" in youtube_link:
            self.download_mp4_playlist(youtube_link, pathism)
        else:
            self.download_mp4_single(youtube_link, pathism)



    def download_differ(self, event):
        current_mp = self.mp3_vs_mp4.get()
        print(f'current_mp: {current_mp}')
        if current_mp == ".MP?":
            print("stupid head")
        elif current_mp == ".MP3":
            self.download_mp3_differ()
        else:
            self.download_mp4_differ()


    def yt_link_get_thread(self, *event):
        thread1 = threading.Thread(target=self.yt_link_get)
        thread1.start()


    def clear_youtubebox(self):
        self.YOUTUBEBOX.delete(0, 'end')



    def yt_link_get(self, *event):
        ytlink = self.yt_link_stringvar.get()
        self.download_differ(ytlink)
        self.YOUTUBEBOX.delete(0, 'end')

    def on_page_swap(self, event):
        with open("./Cache/downloadlocation.json", 'r') as file:
            new_json = json.load(file)
            self.desire_path.configure(values=new_json)
            self.desire_path.set(new_json[0])



class import_music:
    def __init__(self, Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid):
        self.Title = Title
        self.Author = Author
        self.Album = Album
        self.SavelocationThumb = SavelocationThumb
        self.Savelocation = Savelocation
        self.Uniqueid = Uniqueid

    def __repr__(self):
        return f"{self.Title} {self.Author} | "

# TODO should probably reformat this class at some point :( works fine for now tho !
class active_playlist(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        self.controller = controller
        button_main = Button(self, text="Main page", command=lambda: controller.show_frame(Main_page))
        button_current = Button(self, text="Currently playing", command=lambda: controller.show_frame(Currently_playing))
        button_download = Button(self, text="Download", command=lambda: controller.show_frame(Download))
        button_settings = Button(self, text="Settings", command=lambda: controller.show_frame(Settings))
        button_mp4 = Button(self, text="Video downloader", command=lambda: controller.show_frame(mp4_downloader))
        button_main.place(x=0, y=125)
        button_current.place(x=0, y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0, y=200)
        button_mp4.place(x=0, y=225)
        play_playlist_button = Button(self, text="play!", command=self.play_playlist)
        play_playlist_button.place(x=250, y=25)
        self.bind("<<ShowFrame>>", self.on_page_begin)
        self.playlist = ''
        print(f'global playlist right before used: {self.controller.shared_data["playlist"]}')
        self.playlist_frame = Frame(self)
        self.playlist_frame.place(x=110, y=100)
        self.song_menu = Menu(self.playlist_frame, tearoff=0)
        playlist_submenu = Menu(self.song_menu)
        for playlist_name in self.query_all_playlists(): #inherits last one. all 1 command. want seperate if access quer() with [0]. iterator!
            playlist_submenu.add_command(label=playlist_name, command=lambda playlist_name=playlist_name: self.add_to_playlist(playlist_name))
        self.song_menu.add_cascade(label="Add to:", menu=playlist_submenu)
        self.song_menu.add_command(label="Play", command=lambda: self.play_playlist("y"))
        self.song_menu.add_command(label="Rename", command=lambda: self.popup_rename("x"))
        self.song_menu.add_command(label="Delete", command=self.differ_delete)
        self.song_menu.add_command(label="Rename Multiple", command=lambda: self.popup_rename_multiple("x"))
        self.song_menu.add_command(label="Test type", command=self.play_specifically)
        self.playlist_title = ttk.Label(self, textvariable=self.controller.shared_data['playlist'], anchor="center",
                                        background='#272c34', font=('Arial', 40))
        self.playlist_title.place(y=15, x=100)
        playlist_scroll = Scrollbar(self.playlist_frame)
        playlist_scroll.pack(side=RIGHT, fill=Y)
        style = ttk.Style()
        style.configure("mystyle.Treeview", font=('Calibri', 11), foreground='white', background='#262626')
        style.configure("mystyle.Treeview.Heading", font=('Times New Roman', 15), foreground='#262626', bg='blue')
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        self.playlist_table = ttk.Treeview(self.playlist_frame, yscrollcommand=playlist_scroll.set, xscrollcommand=playlist_scroll.set,
                             style="mystyle.Treeview", height=20)
        self.playlist_table.bind("<Button-3>", self.popup_event)
        style.map('Treeview', background=[('selected', '#3f5e91')])
        playlist_scroll.config(command=self.playlist_table.yview)  # ability to scroll down
        self.playlist_table['columns'] = ('Artist', 'Song', 'Album')
        self.playlist_table.column("#0", width=0, stretch=NO)
        self.playlist_table.column('Artist', anchor=CENTER, width=250, stretch=NO)
        self.playlist_table.column('Song', anchor=CENTER, width=250, stretch=NO)
        self.playlist_table.column('Album', anchor=CENTER, width=200, stretch=NO)
        self.playlist_table.heading("#0", text='', anchor=CENTER)
        self.playlist_table.heading('Artist', text="Artist", anchor=CENTER)
        self.playlist_table.heading('Song', text="Song", anchor=CENTER)
        self.playlist_table.heading('Album', text='Album', anchor=CENTER)
        self.playlist_table.pack(expand=True, ipady="75")
        self.new_frame = lambda: controller.show_frame(Currently_playing)
        self.re_query_all()

    def play_playlist(self):
        print(f'is_playing: {everyones_music.thr.is_alive()}')
        print(f'global playlistrn: {self.controller.shared_data["playlist"]}')
        everyones_music.query_list()
        print("CALLED BY play_playlist")
        everyones_music.play()
        self.new_frame()

    def play_specifically(self):
        for y in self.playlist_table.selection():
            chosen_song = self.playlist_table.item(y, 'values')
            print(f'chosen_song = {chosen_song}')
            print(f'choosen playlist! {self.playlist}')
            self.controller.music_obj = {
                import_music(chosen_song[0], chosen_song[1], chosen_song[2], chosen_song[3], chosen_song[4],
                             chosen_song[5])
            }
            self.controller.shared_data['playlist'] = self.playlist
            everyones_music.query_list()
            for entry in everyones_music.current_playlist:
                if entry.Uniqueid == chosen_song[5]:
                    new_song = everyones_music.current_playlist.index(entry)
                    everyones_music.song_count = new_song
            everyones_music.play()




    def shown(self, event):
        print("New thingy shown")

    def on_page_begin(self, event):
        # Deletes all of the current data in the Treeview
        self.playlist_table.delete(*self.playlist_table.get_children())
        # Sets the viewing playlist equal to the playlist set when clicking the right menu (defined in switch_to_playlis
        # We also use [0] because it returns the data as a tuple with 1 entry.
        self.playlist = self.controller.viewed_playlist[0]
        # Re-queries the list to show what user clicked on (right menu)
        self.new_query_all("event")
        # query is done so that playing a specific song is allowed to pick and choose from the list of objects
        # and remove the one selected, and place at begining


    def new_query_all(self, event):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(f'gbl playlist type: {type(self.controller.shared_data["playlist"])}:'
              f' {self.controller.shared_data["playlist"]}')
        print(f'self.playlist = {self.playlist}')
        cur1.execute("SELECT Author, Title, Album, Savelocation, SavelocationThumb, Uniqueid FROM {}".format(
            self.playlist))
        # from 'main' need to inherit from a selelection from mainpage that includes a playlistname
        rows = cur1.fetchall()
        for row in rows:
            #print(f'row: {row}')
            self.playlist_table.insert('', tk.END, values=row)
        con1.close()



    def query_all(self, event):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(f'playlist playlist type: {type(self.controller.shared_data["playlist"])}: {self.controller.shared_data["playlist"]}')
        cur1.execute("SELECT Author, Title, Album, Savelocation, SavelocationThumb, Uniqueid FROM {}".format(
            self.controller.shared_data["playlist"]))
        # from 'main' need to inherit from a selelection from mainpage that includes a playlistname
        rows = cur1.fetchall()
        for row in rows:
            self.playlist_table.insert('', tk.END, values=row)
        con1.close()
    def query_all_playlists(self):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        cur1.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = cur1.fetchall()
        return rows

    def add_to_playlist(self, playlist): #*kwargs should be music objects
        print(f'passed in playlist: {playlist}, play[0]={playlist[0]}')
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        selected_songs = self.playlist_table.selection()
        print(playlist)
        for item in selected_songs:
            song_broken_down = self.playlist_table.item(item, 'values')
            print(f'title?: {song_broken_down[0]}, author:{song_broken_down[1]}, saveloc:{song_broken_down[2]}, thumbnail:{song_broken_down[3]}, album:{song_broken_down[4]}, id:{song_broken_down[5]}')
            print(f'song_suple: {item}')

            #print(f'selected_songs: {selected_songs}')
            #song_tuple = self.playlist_table.item(selected_songs, 'values')
            cur1.execute("INSERT INTO {} VALUES (?,?,?,?,?,?)".format(playlist[0]), (song_broken_down[1], song_broken_down[0], song_broken_down[3], song_broken_down[4], song_broken_down[2], song_broken_down[5]))
        con1.commit()


    def un_query_all(self):
        self.playlist_table.delete(*self.playlist_table.get_children())

    def differ_delete(self):
        print(f'gbl in differ: {self.controller.shared_data["playlist"]}')
        if self.playlist == 'main':
            self.full_delete_multiple()
        else:
            self.half_delete_multiple()

    # Deletion mode?
    def full_delete_multiple(self):
        print('using full delete!')
        selection_items = self.playlist_table.selection()
        final_chance = tk.messagebox.askokcancel(title="Are you sure?", message="This will permanently delete all"
                                                                             " selected!")
        if final_chance is True:
            for item in selection_items:
                multiple_id = (self.playlist_table.item(item)['values'])
                self.delete_from_db(multiple_id[5], multiple_id[1])
                self.playlist_table.delete(item)
                os.remove(multiple_id[3])
                os.remove(multiple_id[4])

    def half_delete_multiple(self):
        print('using half_delete!')
        selection_items = self.playlist_table.selection()
        for item in selection_items:
            multiple_id = (self.playlist_table.item(item)['values'])
            self.delete_from_db(multiple_id[5], multiple_id[1])
            self.playlist_table.delete(item)

    def delete_from_db(self, new_id, song_named):
        connect1 = sqlite3.connect('MAINPLAYLIST.sqlite')
        concur2 = connect1.cursor()
        print(f'deleting: {song_named}')
        print(f'globalplaylist: {self.controller.shared_data["playlist"]} {type(self.controller.shared_data["playlist"])}')
        print(f'new_id: {new_id}')
        concur2.execute("DELETE FROM {} WHERE Uniqueid=?".format(self.playlist), (new_id,))
        connect1.commit()
        concur2.close()


    def popup_event(self, event):
        print("CLICKED!!!")
        try:
            self.song_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.song_menu.grab_release()

    def popup_rename(self, event):
        popup_rename_window = Toplevel(self)
        popup_rename_window.geometry("250x250+125+235") #TODO styling to not look terrible lol
        popup_rename_window.title("Rename :D")
        selected = self.playlist_table.focus()
        selected_song = self.playlist_table.item(selected, 'values')
        for items in selected_song:
            print(items)
        print(selected_song[1])
        song_id = selected_song[5]

        def destroy_popup(event):
            popup_rename_window.destroy()
            popup_rename_window.update()

        author_rename_label = Label(popup_rename_window, text="Author").pack()
        author_rename_entry = Entry(popup_rename_window)
        author_rename_entry.insert(END, selected_song[0])
        author_rename_entry.pack()
        title_rename_label = Label(popup_rename_window, text="Title").pack()
        title_rename_entry = Entry(popup_rename_window)
        title_rename_entry.insert(END, selected_song[1])
        title_rename_entry.pack()
        album_rename_label = Label(popup_rename_window, text="Album").pack()
        album_rename_entry = Entry(popup_rename_window)
        album_rename_entry.insert(END, selected_song[2])
        album_rename_entry.pack()
        instruction_label = Label(popup_rename_window, text='Click "Enter" to confirm!')
        instruction_label.pack()

        def rename_entry(event):
            new_author = author_rename_entry.get()
            new_title = title_rename_entry.get()
            new_album = album_rename_entry.get()
            self.playlist_table.item(selected, text="",
                       values=(
                       new_author, new_title, new_album, selected_song[3], selected_song[4], selected_song[5]))

        def rename_destroy_combine_thr(event):
            thr = threading.Thread(target=rename_destroy_combine)
            thr.start()

        def rename_destroy_combine():
            rename_entry("event")
            change_database_entry("event")
            destroy_popup("event")

        def change_database_entry(event):
            connect1 = sqlite3.connect('./MAINPLAYLIST.sqlite')
            concur2 = connect1.cursor()
            # concur2.execute("UPDATE FROM main WHERE Uniqueid=?", (song_id,)) guess
            update_author = author_rename_entry.get()
            update_title = title_rename_entry.get()
            update_album = album_rename_entry.get()
            retain_download_jpg = selected_song[3]
            retain_download_mp3 = selected_song[4]
            concur2.execute(
                "UPDATE main SET Author=?, Title=?, Album=? , Savelocation=?, SavelocationThumb=? WHERE Uniqueid=?",
                (update_author, update_title, update_album, retain_download_jpg, retain_download_mp3, song_id,))

            connect1.commit()
            connect1.close()


        popup_rename_window.bind("<Return>", rename_destroy_combine_thr)

    def popup_rename_multiple(self, event):
        popup_rename_multiple_window = Toplevel(self)
        popup_rename_multiple_window.geometry("250x250+125+235")
        popup_rename_multiple_window.title("Rename Multiple :D")
        all_selected = self.playlist_table.selection()
        selected_song = ''
        for one_song in all_selected:
            selected_song = self.playlist_table.item(one_song, 'values')
            print(f'selcted: {all_selected}')
            print(f'artist, album: {selected_song[0]}, {selected_song[2]}')

        def destroy_multiple_popup(event):
            popup_rename_multiple_window.destroy()
            popup_rename_multiple_window.update()
            # Rename Multiple Entry

        # Rename Multiple Entry
        Label(popup_rename_multiple_window, text="Author").pack()
        author_rename_entry = Entry(popup_rename_multiple_window)
        author_rename_entry.pack()
        Label(popup_rename_multiple_window, text="Album").pack()
        album_rename_entry = Entry(popup_rename_multiple_window)
        album_rename_entry.pack()
        # Filling it with the data
        author_rename_entry.insert(END, selected_song[0])
        album_rename_entry.insert(END, selected_song[2])
        #The entry boxes should remain empty, as multiple entries could have a differnt values. so none added

        def multiple_rename_entry(*event):
            new_author = author_rename_entry.get()
            new_album = album_rename_entry.get()
            all_selected = self.playlist_table.selection()
            for one_song in all_selected:
                selected_song = self.playlist_table.item(one_song, 'values')
                print(f'selcted: {all_selected}')
                print(f'selected_song: {selected_song}')
                self.playlist_table.item(one_song, text='', values=(new_author, selected_song[1], new_album, selected_song[3], selected_song[4], selected_song[5]))
                change_database_entry_multiple("event", selected_song)

        def rename_multiple_destory_combine(event):
            multiple_rename_entry("event")
            change_database_entry_multiple("event", selected_song)  # CREATE ONE
            destroy_multiple_popup("event")

        def change_database_entry_multiple(event, passed_in_song):
            connect1 = sqlite3.connect('./MAINPLAYLIST.sqlite')
            concur2 = connect1.cursor()
            update_author = author_rename_entry.get()
            update_album = album_rename_entry.get()
            retain_title = passed_in_song[1]
            retain_download_jpg = passed_in_song[4]
            retain_download_mp3 = passed_in_song[3]
            retain_song_id = passed_in_song[5]
            concur2.execute(
                "UPDATE main SET Author=?, Title=?, Album=? , Savelocation=?, SavelocationThumb=? WHERE Uniqueid=?",  #I would want to say that this doesnt reapply 'Uniqueid' but idk
                (update_author, retain_title, update_album, retain_download_mp3, retain_download_jpg, retain_song_id,))

            connect1.commit()
            connect1.close()
        popup_rename_multiple_window.bind("<Return>", rename_multiple_destory_combine)

        song_menu = Menu(self.playlist_table, tearoff=0)


        playlist_submenu = Menu(song_menu)
        for playlist_name in self.query_all_playlists(): #inherits last one. all 1 command. want seperate if access quer() with [0]. iterator!
            playlist_submenu.add_command(label=playlist_name, command=lambda playlist_name=playlist_name: self.add_to_playlist(playlist_name))




        song_menu.add_cascade(label="Add To:", menu=playlist_submenu)
        song_menu.add_command(label="Rename", command=lambda: self.popup_rename("x"))
        song_menu.add_command(label="Delete", command=self.differ_delete)
        song_menu.add_command(label="Rename Multiple", command=lambda: self.popup_rename_multiple("x"))
        self.playlist_table.bind("<Button-3>", self.popup_event)
        self.playlist_table.bind("<Delete>", self.differ_delete)

    def re_query_all(self):
        self.un_query_all()
        self.query_all("event")
        print(f"requireed! global_playlist: {self.controller.shared_data['playlist']}")


        button_refresh = Button(self, text='Refresh', command=self.re_query_all)
        button_refresh.place(x=10, y=10)


# This class is very buggy but is the best way to make the volume work
class AudioController:
    def __init__(self, process_name):
        self.process_name = process_name
        self.volume = self.process_volume()

    def process_volume(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                return interface.GetMasterVolume()

    def set_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # only set volume in the range 0.0 to 1.0
                self.volume = min(1.0, max(0.0, decibels))
                interface.SetMasterVolume(self.volume, None)

    def increment_volume(self, decibels):
        decibels = self.process_volume()
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # only set volume in the range 0.0 to 1.0
                self.volume = min(1.0, max(0.0, (decibels + .01)))
                interface.SetMasterVolume(self.volume, None)
                print(f"volume set to: {self.volume}")

    def decrease_volume(self, decibels):
        decibels = self.process_volume()
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # only set volume in the range 0.0 to 1.0
                self.volume = min(1.0, max(0.0, (decibels - .01)))
                interface.SetMasterVolume(self.volume, None)
                print(f"volume set to: {self.volume}")


    def mute_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                self.volume = 0
                interface.SetMasterVolume(self.volume, None)
def volume_slider_controller(event):
    audio_controller = AudioController("python.exe") #will need to be punge.exe
    audio_controller.set_volume(float(event))
    audio_controller.process_volume()


def volume_mute():
    audio_control = AudioController("python.exe")
    audio_control.set_volume(0)
    audio_control.process_volume()


def static_increment_bind(extra=None):
    audiocontroller = AudioController("python.exe")
    audiocontroller.increment_volume("ok")


def static_decrease_bind(extra=None):
    audiocontroller = AudioController("python.exe")
    audiocontroller.decrease_volume("ok")


main_app = tkinter_main()
main_app.mainloop()
