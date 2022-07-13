import tkinter
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import tkinter as tk
import os
import sqlite3
#from PIL import Image, ImageTk
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
import simpleaudio as sa
from pydub.playback import play
from pathlib import Path
import random
from pycaw.pycaw import AudioUtilities
import sys
from system_hotkey import SystemHotkey
global_hotkey = SystemHotkey()


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

pydub.AudioSegment.converter = r"F:\Support files\Super random\the crossfade\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
pydub.AudioSegment.ffprobe = r"F:\Support files\Super random\the crossfade\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\ffprobe.exe"

class music_player:
    song = None
    start_time = 0
    now_time = 0
    thr = threading.Thread()
    song_count = 0
    sleeptimer = 0
    current_playlist = []
    resume_list = []
    shuffle = True
    exited = threading.Event()
    coming_from_loop = True
    pause_bool = False
    is_playing = False
    # Shuffle switch is for when a playlist is queried and user either goes from shuffle -> non-shuffle or vice versa
    # Need to be able to detect if shuffle was swapped. if shuffle was on: get current song's id. reqeury playlist and
    # Go to that position. if shuffle is off: next song will shuffle.
    shuffle_switch = False

    def pause_play_toggle(self, extra=None):
        # If it is pausued:
        if self.pause_bool is True:
            everyones_music.thud2()
            self.pause_bool = False
        else:
            self.pause_bool = True
            everyones_music.stop()
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



    def stop_timer(self):
        self.now_time = time.time() - self.start_time
        self.now_time = round(self.now_time, 3)
        print(f"Now time: {self.now_time}")
        self.resume_list.append(self.now_time)
        total_time = 0
        for time_seg in self.resume_list:
            total_time += time_seg
        print(f'TOTAL_TIME: {total_time}')
        self.coming_from_loop = False



    def start_test_loop(self):
        while not self.exited.is_set():
            self.say_hi()
            # The timer for the song, length of song
            self.exited.wait(1)
            print("end of test_loop")

    def quit_out(self, signo=0, _frame=0):
        print("interupted by ", signo)
        self.exited.set()
        self.stop()
        self.exited.clear()

    def thrd(self):
        if self.thr.is_alive() is True:
            print("SONG IS ALREADY PLAYING. NOW STOPPING IT")
            everyones_music.stop()
            time.sleep(.5)
            #everyones_music.reset_class_defaults()
            print("THRD!")
            self.is_playing = True
            self.exited.clear()
            self.thr = KThread(target=self.testsong)
            self.thr.start()
        else:
            print("THRD!")
            self.is_playing = True
            self.exited.clear()
            self.thr = KThread(target=self.testsong)
            self.thr.start()

    def say_hi(self):
        print("HI from say_hi()")
        time.sleep(1)
        print("end of say_Hi")

    def thud(self):
        print("called thud!")

        self.thr = KThread(target=self.testsong)
        self.thr.start()
        self.thr.join()

    def thud2(self):
        self.is_playing = True
        self.thr = KThread(target=self.resume)
        self.thr.start()
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
            self.song = AudioSegment.from_file(self.current_playlist[self.song_count].Savelocation)
            self.main_music_loop()
        else:
            self.main_music_loop()


    def main_music_loop(self):
        #self.is_playing = True
        self.print_debug("main_music_loop")
        # Used to reset the flag to neutral. Redundant for 'first time play' but useful after a pause
        # self.exited.clear()
        if self.coming_from_loop is True:
            self.resume_list.clear()
        while not self.exited.is_set():
            # Reset True status so if resume isn't called (sets to false) the resume_list is cleared
            self.coming_from_loop = True
            try:
                # Plays said audio segment
                self.start_time = time.time()
                self.playback = pydub.playback._play_with_simpleaudio(self.song)
                # Adjusting the class variables for next time the loop runs
                self.sleeptimer = self.song.duration_seconds
                # Defines next song in rotation (based on incrementing number in list index)
                self.song_count = self.song_count + 1
                # Begins class variable timer. Uses so resume() knows where to pick up from
                # Essentially time.sleep() but can be interupted by flags ( self.exited.is_set() )
                print(f'current song: {self.current_playlist[self.song_count - 1].Title} sngcount: {self.song_count-1}')
                self.exited.wait(self.sleeptimer)
                # Creates the audiosegment from the new song
                self.song = AudioSegment.from_file(self.current_playlist[self.song_count].Savelocation)
                # Makes the resume will make this false if called, else: it'll clear the list each time
                self.coming_from_loop = True
            except IndexError:
                self.song_count = self.song_count + 1
                self.main_music_loop()


    def sleep_check(self):
        print("begin sleep")
        time.sleep(10)
        print("end sleep!")

    def list_debug(self):
        print("PLAYLIST:")
        for item in self.current_playlist[self.song_count:self.song_count + 5]:
            print(item.Title)

    def debug(self):
        print("-----DEBUG----")
        print(self.song)
        print(self.start_time)
        print(self.now_time)
        print(self.thr)
        print(self.song_count)
        print(self.sleeptimer)
        print(self.current_playlist)
        print(self.resume_list)
        print(self.shuffle)
        print(self.exited)
        print(self.coming_from_loop)
        print(self.pause_bool)
        # print(self.is_playing) is_playing is now legacy. thr.is_alive() is 9x more consistant
        print(f'is thread active?: {self.thr.is_alive()}')
        print(f'is playing: {self.is_playing}')
        print("-----DEBUG----")

    def reset_class_defaults(self):
        print('reset defaults called')
        #self.stop()
        self.song = None
        self.start_time = 0
        self.now_time = 0
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



    def stop(self):
        self.is_playing = False
        print(type(self.now_time), type(self.start_time))
        self.now_time = time.time() - self.start_time
        now_time = round(self.now_time, 3)
        self.exited.set()
        self.playback.stop()
        # Needed to reset the exited timer. One to flick it, one to reset to neutral
        self.exited.set()
        self.print_debug("stop")

    def skip_forwards(self, option=None):
        if self.pause_bool is False:
            # Kills the self.exited.wait() timer
            self.exited.set()
            # Kills the audiosegment playing
            self.stop()
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
            self.thrd()
            self.pause_bool = False



    def print_debug(self, call_method):
        print(f'called by:  {call_method}')
        print(f'self.thr: {self.thr}')
        print(f'self.exited.isSet bool: {self.exited.is_set()}')
        print(f'self.pause_bool: {self.pause_bool}')
        print(f'self.coming_from_loop: {self.coming_from_loop}')
        print('\n \n')




    def skip_backwards(self, option=None):
        if self.song_count == 1:
            pass
        else:
            if self.pause_bool is False:
                self.exited.set()
                self.song_count = self.song_count - 2
                self.stop()
                self.exited.clear()
                self.resume_list.clear()
            else:
                self.exited.clear()
                self.resume_list.clear()
                self.song_count = self.song_count - 2
                self.thrd()
                self.pause_bool = False
    """
fix for resuming not working:
problem: Each time pause occurs, the self.start_song gets reset. this causes 'segmentation' of the song
where it doesnt account for the time.time() when it should be the beginning of the song (the time difference
should be a when the song began vs when it was most recently paused. 
Solution:
    create class list
    append time of each interval into class list
    this time ^ should be the time between the song beginning (again after a pause too) and when it is paused
    this added-up time should not exceed the length of the song and should add up to where user paused last
    the result of the list should be passed into self.testsong and likely calculated in self.ressume
    """
    def add_times(self):
        to_return = 0
        for item in self.resume_list:
            to_return += item
        return to_return


    def resume(self):
        print("##RESUME##")
        self.exited.clear()
        print(f'index at beginning of resume() {self.song_count}')
        # Makes it replay the song that was just stopped (offsetting the +1 form the original function)
        self.song_count = self.song_count - 1
        self.song = AudioSegment.from_file(self.current_playlist[self.song_count].Savelocation)
        print(f'resume count: {self.song_count}')
        #print(f'nowtime: {now_time}')
        # Current time in miliseconds (metric pydub operates in)
        self.now_time = self.now_time * 1000
        self.resume_list.append(self.now_time)
        print(f'now_time before usage: {self.now_time}')
        new_time = 0
        for time_item in self.resume_list:
            new_time += time_item
        print(f'Size of new_time: {new_time}')
        # Defines class variable as only a portion of a song
        self.song = self.song[new_time:]
        print(f'main_part (resume): {type(self.playback)}')
        self.coming_from_loop = False
        self.testsong("yella")
        print(f'index at end of resume() {self.song_count}')


    def query_list(self, list_of_choice):
        new_list = list_of_choice.replace(" ", "_")
        big_ol_list = []
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        mex = cur1.execute("SELECT Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid FROM {}".format(new_list))
        rows = cur1.fetchall()
        for each in rows:
            imported_music = import_music(*each)
            big_ol_list.append(imported_music)
        print(f'self.shuffle: {self.shuffle}')
        if self.shuffle is True:
            random.shuffle(big_ol_list)
        elif self.shuffle_switch is True:
            self.shuffle_switch = False
            index_id = self.current_playlist[self.song_count]
            for entry in self.current_playlist:
                if entry.Uniqueid == index_id.Uniqueid:
                    new_song = self.current_playlist.index(entry)
                    self.song_count = new_song
        self.current_playlist = big_ol_list

    def update_playlist(self):
        if self.shuffle is True:
            self.scramble_playlist()
            self.shuffle = False
        else:
            self.reassemble_list()
            self.shuffle = True


    def scramble_playlist(self):
        random.shuffle(self.current_playlist)


    def reassemble_list(self):
        # Grabs the id of current song to begin at.
        try:
            index_id = self.current_playlist[self.song_count - 1].Uniqueid
        except IndexError:
            self.query_list('main')
            index_id = self.current_playlist[0].Uniqueid
        print(f"Should be current song: {self.current_playlist[self.song_count].Title}")
        # turns self.current_playlist into an unscrambled version
        self.query_list(global_playlist.get())
        # Iterate over each entry of said playlist
        for entry in self.current_playlist:
            # Find where the current song sits in the unqueried list, set song_count to that number
            if entry.Uniqueid == index_id:
                print(f"current song to grab is: {entry.Title}")
                x = self.current_playlist.index(entry)
                # +1 required because when index is got, it will get the index of the active, playing song. we want it
                # to play the next song up.
                self.song_count = x + 1


everyones_music = music_player()


# Initialized


class tkinter_main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1250x750+125+100")
        self.resizable(False, False)
        self.configure(bg="#272c34")
        self.title("Punge Testing")
        self.iconbitmap("./punge icon.ico")
        self.option_add('*tearOff', FALSE)
        # self.properclose required for the app to stop playing music on exit
        self.protocol("WM_DELETE_WINDOW", self.proper_close)
        main_page_frame = tk.Frame(self)
        main_page_frame.pack(side="top", fill="both", expand=True)
        main_page_frame.grid_rowconfigure(0, weight=1)
        main_page_frame.grid_columnconfigure(0, weight=1)
        right_frame = ttk.Style()
        right_frame.configure('TFrame', background='#262626')
        tk.Button(self, text='DEBUG !', command=everyones_music.debug).place(x=100, y=10)
        tk.Button(self, text='Playlist debug', command=everyones_music.list_debug).place(x=100, y=40)
        self.root_frame = ttk.Frame(self, style='TFrame', height=1000, width=200)
        self.root_frame.place(x=1050, y=0)
        self.frames = {}
        for each_frame in (Main_page, Currently_playing, Settings, Download, mp4_downloader, active_playlist):
            frame = each_frame(main_page_frame, self)
            self.frames[each_frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Main_page)
        # Global hotkeys for ease of use :D. Should be adjustable and configurable
        # binds also need to be able to configure buttons to change states. Like text=shuffle or text=not shuffle.
        global_hotkey.register(['control', 'right'], callback=everyones_music.skip_forwards)
        global_hotkey.register(['control', 'left'], callback=everyones_music.skip_backwards)
        global_hotkey.register(['control', 'end'], callback=everyones_music.pause_play_toggle)
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
        global global_playlist
        global_playlist.set(playlist_in[0])
        self.show_frame(active_playlist)


    def proper_close(self):
        try:
            everyones_music.stop()
        finally:
            sys.exit(10)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
    def get_page(self, page_class):
        return self.frames[page_class]


class Main_page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        self.playlist_frame = Frame(self)
        self.playlist_frame.place(x=185, y=100)
        self.playlist_scroll = Scrollbar(self.playlist_frame)
        self.playlist_scroll.pack(side=RIGHT, fill=Y)
        self.style = ttk.Style()
        self.style.configure("mystyle.Treeview", font=('Calibri', 11), foreground='white', background='#262626')
        self.style.configure("mystyle.Treeview.Heading", font=('Times New Roman', 15), foreground='#262626', bg='blue')
        self.style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        self.test1 = ttk.Treeview(self.playlist_frame, yscrollcommand=self.playlist_scroll.set, xscrollcommand=self.playlist_scroll.set, style="mystyle.Treeview", height=20)
        self.style.map('Treeview', background=[('selected', '#3f5e91')])
        self.playlist_scroll.config(command=self.test1.yview)  # ability to scroll down
        self.test1['columns'] = ('Image', 'Title', 'Description')
        self.test1.column("#0", width=0, stretch=NO)
        self.test1.column('Image', anchor=CENTER, width=100)
        self.test1.column('Title', anchor=CENTER, width=225)
        self.test1.column('Description', anchor=CENTER, width=250)
        self.test1.heading("#0", text='', anchor=CENTER)
        self.test1.heading('Image', text="Image", anchor=CENTER) #Remove this & 2 below after. exists for debugging purposes
        self.test1.heading('Title', text="Title", anchor=CENTER)
        self.test1.heading('Description', text='Description', anchor=CENTER)
        self.test1.pack(expand=True, ipady="75")
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
        button_refresh = Button(self, text='Refresh', command=self.refresh_query)
        button_refresh.place(x=585, y=10)
        button_mp4.place(x=0, y=225)
        button_make_main_table = Button(self, text="TRY NEW PLAYLIST", command=self.create_new_table)
        button_make_main_table.place(relx=.5, rely=.6)

        Button(self, text='reset class defaults', command=self.reseter).place(x=100, y=500)

        self.song_menu = Menu(self.test1, tearoff=0)
        self.song_menu.add_command(label="Play", command=lambda: self.play_playlist("y"))
        self.song_menu.add_command(label="Rename", command=lambda: self.popup_rename("x"))
        self.song_menu.add_command(label="Edit Name", command=self.change_options)
        self.song_menu.add_command(label="Rename Multiple", command=lambda: self.popup_rename_multiple("x"))
        self.test1.bind("<Button-3>", self.popup_event)
        self.test1.bind("<Button-2>", lambda e: self.play_playlist("plaeholder for playlistname"))
        self.test1.bind("<Double-Button-1>", self.view_playlist)
        #self.bind("<Return>", bind_test)
        #self.entry1.delete(0, 'end)
        self.query_all_playlists()
        global global_playlist
        global_playlist = StringVar()
        global_playlist.set('main')

        #Needs to be here cause of reefernce b4 all other functions
    def switch_page(self):
        new_page = self.controller.get_page(active_playlist)
        new_page.query_all("event")

    def create_new_table(self):
        popup_rename_window = Toplevel(self)
        popup_rename_window.geometry("250x250+125+235")
        popup_rename_window.title("")
        new_playlist_name = StringVar()
        playlist_entry = Entry(popup_rename_window, textvariable=new_playlist_name)
        playlist_entry.place(relx=.5, rely=.75)
        playlist_create = Button(popup_rename_window, text="Create!!", command=lambda: create_playlist_combine(playlist_entry.get()))
        playlist_create.place(rely=.5, relx=.5)

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



    def refresh_query(self):
        self.un_query_all()
        self.query_all_playlists()

    def query_all_playlists(self):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        cur1.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = cur1.fetchall()
        for row in rows:
            for super_row in row:
                new_row = super_row.replace("_", " ")
                self.test1.insert('', tk.END, values=(new_row,))
                #print(f'row: {super_row}')

        con1.close()

    def un_query_all(self):
        self.test1.delete(*self.test1.get_children())


    def change_options(self): #Deleting should exist in a 'deleting mode', should change the background color of TREEVIEW
        selection_playlist = self.test1.selection()
        print(selection_playlist)


    def popup_event(self, event):
        try:
            self.song_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.song_menu.grab_release()

    def popup_rename(self, event):
        popup_rename_window = Toplevel(self)
        popup_rename_window.geometry("250x250+125+235") #TODO styling to not look terrible lol
        popup_rename_window.title("Rename :D")
        selected = self.test1.focus()
        selected_song = self.test1.item(selected, 'values')
        for items in selected_song:
            print(f'items={items}')
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

        def rename_entry(event):
            new_author = author_rename_entry.get()
            new_title = title_rename_entry.get()
            new_album = album_rename_entry.get()
            self.test1.item(selected, text="",
                       values=(
                       new_author, new_title, new_album, selected_song[3], selected_song[4], selected_song[5]))


    def popup_rename_multiple(self, event):
        popup_rename_multiple_window = Toplevel(self)
        popup_rename_multiple_window.geometry("250x250+125+235")
        popup_rename_multiple_window.title("Rename Multiple :D")
        all_selected = self.test1.selection()
        for one_song in all_selected:
            selected_song = self.test1.item(one_song, 'values')
            print(f'selcted: {all_selected}')
            print(f'selected_song: {selected_song}')

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
        #The entry boxes should remain empty, as multiple entries could have a differnt values. so none added

    def main_page_music_multithread(self, playlist):
        print(f'playlist?: {playlist}')
        thren = threading.Thread(target=self.playmusic, args=playlist)
        thren.start()

    def reseter(self):
        everyones_music.reset_class_defaults()

    def playmusic(self, playlist_in):
        print(f'playmusic: is_playing: {everyones_music.is_playing}')
        if everyones_music.thr.is_alive() is True:
            everyones_music.stop()
            time.sleep(10)
        everyones_music.reset_class_defaults()
        everyones_music.query_list(playlist_in)
        print("playmusic")
        everyones_music.thrd()

    def play_playlist(self, xia):
        certain_playlist = self.test1.selection()
        if everyones_music.thr.is_alive() is True:
            print('calling stop on everyones_music')
            everyones_music.stop()
        for item in certain_playlist:
            selected_playlist = self.test1.item(item, 'value')
            print(f'selected_playlist: {selected_playlist}')
            print(f'item: {item}')
            print(f'certain_playlist: {certain_playlist}')
            self.main_page_music_multithread(selected_playlist)

        print("Line 254")


    def view_playlist(self, evebt):
        self.controller.show_frame(active_playlist)
        for item in self.test1.selection():
            print(f"debug: item {item}")
            print(f'debug test1.selection: {self.test1.selection()}')
            real_playlist = self.test1.item(item, 'values')
            real_real_playlist = ''.join(real_playlist)
            real_real_real_playlist = real_real_playlist.replace(" ", "_")
            global global_playlist
            global_playlist.set(real_real_real_playlist)
            print(f'gbl playlist: (view_playlist): {global_playlist}')

    def query_all(self, event):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(f'THIS MESS UP?: (query_all): {global_playlist}')
        cur1.execute(
            "SELECT Author, Title, Album, Savelocation, SavelocationThumb, Uniqueid FROM {}".format(
                global_playlist.get()))
        # from 'main' need to inherit from a selelection from mainpage that includes a playlistname
        rows = cur1.fetchall()
        for row in rows:
            self.playlist_table.insert('', tk.END, values=row)
        con1.close()



        #This is where entries for the page goes
        # command=lambda: controller.show_frame(Currently_playing)


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

        self.resume_button = ttk.Button(self, text="TESTING BUTTON", command=self.play_pause_toggle)
        self.resume_button.place(relx=.5, rely=.75)

        self.shuffle_button = ttk.Button(self, text="Shuffle (off)", command=self.shuffle_toggle)
        self.shuffle_button.place(x=250, y=400)

        mute_button = ttk.Button(self, text="mute", command=volume_mute)
        mute_button.place(rely=.5, relx=.65)

        skip_forwards = ttk.Button(self, text="Skip LOL", command=everyones_music.skip_forwards)
        skip_forwards.place(rely=.3, relx=.5)

        skip_backwards = ttk.Button(self, text="Skip back", command=everyones_music.skip_backwards)
        skip_backwards.place(rely=.85, relx=.25)
        everyones_music.shuffle = True
        self.shuffle_toggle()  # Called so it defaults properly

    def resume_pause_update(self):
        self.play_pause_toggle()
        everyones_music.pause_play_toggle()
        self.play_pause_toggle()

    def play_update(self):
        everyones_music.query_list(global_playlist.get())
        print("CALLED BY play_update")
        everyones_music.thrd()

    def play_pause_toggle(self):
        if not everyones_music.thr.is_alive() and not everyones_music.pause_bool:
            self.resume_button.configure(text="Play", command=everyones_music.thrd)
        elif everyones_music.pause_bool is True:
            self.resume_button.configure(text="Resume", command=self.resume_pause_update)
        else:
            print(f'thr_isalive {everyones_music.thr.is_alive()} pausebool: {everyones_music.pause_bool}')
            self.resume_button.configure(text="Stop", command=self.resume_pause_update)

    def shuffle_toggle(self):
        # This controls the entire shuffle system. everytime this button is clicked it will either scramble playlist
        # or find the index of the song relative to the unshuffled playlist and start from there.
        print(f'shuffle: {everyones_music.shuffle}')
        if everyones_music.shuffle is True:
            print("playlist scrambled!")
            self.shuffle_button.configure(text="Shuffle (turn off)")
        else:
            print("list reassemabled!")
            self.shuffle_button.configure(text="shuffle (Turn on)")
        everyones_music.update_playlist()



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



        def download_mp3_playlist(youtube_link, pathism):
            video1 = Playlist(youtube_link)
            for video_main in video1.videos:
                video_sep2 = video_main.streams.get_audio_only()
                bruh_change = video_sep2.download(output_path=pathism)
                pre, ext = os.path.splitext(bruh_change)
                os.rename(bruh_change, pre + ".mp3")

        def download_mp3_single(youtube_link, pathism):
            video1 = YouTube(youtube_link)
            video_main = video1.streams.get_audio_only()
            print(video_main.title)
            bruh_change = video_main.download(output_path=pathism)
            pre, ext = os.path.splitext(bruh_change)
            os.rename(bruh_change, pre + ".mp3")

        def download_mp4_playlist(youtube_link, pathism):
            video1 = Playlist(youtube_link)
            for video_main in video1.videos:
                video_sep2 = video_main.streams.get_highest_resolution()
                video_sep2.download(output_path=pathism)

        def download_mp4_single(youtube_link, pathism):
            video1 = YouTube(youtube_link)
            vid_download = video1.streams.get_highest_resolution()
            print(vid_download.title)
            vid_download.download(output_path=pathism)




        def download_mp3_differ():
            pathism = desire_path.get()
            if os.path.exists(pathism) is False:
                print("Choose a proper path lil bruh")
            else:
                youtube_link = yt_link_stringvar.get()
                if "list=" in youtube_link:
                    download_mp3_playlist(youtube_link, pathism)
                else:
                    download_mp3_single(youtube_link, pathism)
        def download_mp4_differ():
            pathism = desire_path.get()
            youtube_link = yt_link_stringvar.get()
            if "list=" in youtube_link:
                download_mp4_playlist(youtube_link, pathism)
            else:
                download_mp4_single(youtube_link, pathism)



        def download_differ(event):
            current_mp = mp3_vs_mp4.get()
            print(f'current_mp: {current_mp}')
            if current_mp == ".MP?":
                print("stupid head")
            elif current_mp == ".MP3":
                download_mp3_differ()
            else:
                download_mp4_differ()


        def yt_link_get_thread(*event):
            thread1 = threading.Thread(target=yt_link_get)
            thread1.start()

        yt_link_stringvar = StringVar()
        YOUTUBEBOX = ttk.Entry(self, textvariable=yt_link_stringvar)
        YOUTUBEBOX.place(rely=.40, relx=.5, anchor=CENTER, width=250)
        YOUTUBEBOX.bind("<Return>", yt_link_get_thread)

        download_button = ttk.Button(self, text="Get!", command=yt_link_get_thread)
        download_button.place(rely=.45, relx=.5, anchor=CENTER)

        mp3_vs_mp4_list = [".MP?", ".MP3", ".MP4"]
        mp3_vs_mp4 = StringVar()
        mp4_mp3_differ_box = ttk.OptionMenu(self, mp3_vs_mp4, *mp3_vs_mp4_list)
        mp4_mp3_differ_box.place(x=5, y=240)

        desire_path_values = ["f:/downloads folder", "f:/files at random"] #settings add more

        desire_path = ttk.Combobox(self, width=30, values=desire_path_values)
        desire_path.set("C:/")  # Should be settable by user ?
        desire_path.place(relx=.5, rely=.5, anchor=CENTER)

        def yt_link_get(*event):
            ytlink = yt_link_stringvar.get()
            download_differ(ytlink)
            YOUTUBEBOX.delete(0, 'end')



class import_music:
    def __init__(self, Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid):
        self.Title = Title
        self.Author = Author
        self.Album = Album
        self.SavelocationThumb = SavelocationThumb
        self.Savelocation = Savelocation
        self.Uniqueid = Uniqueid

class active_playlist(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
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
        print(f'global playlist right before used: {global_playlist}')
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
        self.playlist_title = ttk.Label(self, textvariable=global_playlist, anchor="center", background='#272c34', font=('Arial', 40))
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

    def play_playlist(self):
        print(f'is_playing: {everyones_music.thr.is_alive()}')
        #everyones_music.reset_class_defaults()
        print(f'global playlistrn: {global_playlist.get()}')
        everyones_music.query_list(global_playlist.get())
        print("CALLED BY play_playlist")
        everyones_music.thrd()
        self.new_frame()



    def play_specifically(self):
        # Choosen song = song user wants to play
        for y in self.playlist_table.selection():
            chosen_song = self.playlist_table.item(y, 'values')
            print(f'z: {chosen_song[5]} in {global_playlist.get()}')
            print(everyones_music.current_playlist)
            for entry in everyones_music.current_playlist:
                if entry.Uniqueid == chosen_song[5]:
                    new_song = everyones_music.current_playlist.index(entry)
                    everyones_music.song_count = new_song
        print("CALLED BY play_specifically")
        everyones_music.thrd()


    def shown(self, event):
        print("New thingy shown")

    def on_page_begin(self, event):
        self.playlist_table.delete(*self.playlist_table.get_children())
        self.new_query_all("event")
        print(f"requireed! global_playlist: {global_playlist}")
        # query is done so that playing a specific song is allowed to pick and choose from the list of objects
        # and remove the one selected, and place at begining
        everyones_music.query_list(global_playlist.get())

    def new_query_all(self, event):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(f'gbl playlist type: {type(global_playlist.get())}: {global_playlist.get()}')
        cur1.execute("SELECT Author, Title, Album, Savelocation, SavelocationThumb, Uniqueid FROM {}".format(
            global_playlist.get()))
        # from 'main' need to inherit from a selelection from mainpage that includes a playlistname
        rows = cur1.fetchall()
        for row in rows:
            #print(f'row: {row}')
            self.playlist_table.insert('', tk.END, values=row)
        con1.close()



    def query_all(self, event):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(f'gbl playlist type: {type(global_playlist.get())}: {global_playlist.get()}')
        cur1.execute("SELECT Author, Title, Album, Savelocation, SavelocationThumb, Uniqueid FROM {}".format(
            global_playlist.get()))
        # from 'main' need to inherit from a selelection from mainpage that includes a playlistname
        rows = cur1.fetchall()
        for row in rows:
            print(f'row: {row}')
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
        print(f'gbl in differ: {global_playlist.get()}')
        if global_playlist.get() == 'main':
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
        # TODO ALWAYS DELETES FROM MAIN I THINK
        print(f'globalplaylist: {global_playlist.get()} {type(global_playlist.get())}')
        print(f'new_id: {new_id}')
        concur2.execute("DELETE FROM {} WHERE Uniqueid=?".format(global_playlist.get()), (new_id,))
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

        def rename_entry(event):
            new_author = author_rename_entry.get()
            new_title = title_rename_entry.get()
            new_album = album_rename_entry.get()
            self.playlist_table.item(selected, text="",
                       values=(
                       new_author, new_title, new_album, selected_song[3], selected_song[4], selected_song[5]))

        def rename_destroy_combine(event):
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


        popup_rename_window.bind("<Return>", rename_destroy_combine)

    def popup_rename_multiple(self, event):
        popup_rename_multiple_window = Toplevel(self)
        popup_rename_multiple_window.geometry("250x250+125+235")
        popup_rename_multiple_window.title("Rename Multiple :D")
        all_selected = self.playlist_table.selection()
        for one_song in all_selected:
            selected_song = self.playlist_table.item(one_song, 'values')
            print(f'selcted: {all_selected}')
            print(f'selected_song: {selected_song}')

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
        song_menu.add_command(label="Delete", command=self.delete_multiple)
        song_menu.add_command(label="Rename Multiple", command=lambda: self.popup_rename_multiple("x"))
        self.playlist_table.bind("<Button-3>", self.popup_event)
        self.playlist_table.bind("<Delete>", lambda e: self.delete_multiple())

        def re_query_all(self):
            self.un_query_all()
            self.query_all("event")
            print(f"requireed! global_playlist: {global_playlist}")


        button_refresh = Button(self, text='Refresh', command=re_query_all)
        button_refresh.place(x=10, y=10)

        re_query_all()

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
