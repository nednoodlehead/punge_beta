from tkinter import ttk
from tkinter import *
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

class music_player:
    current_playing1 = 3
    current_playing2 = 2
    sleeptimer = 0
    inner_playing_loop = True
    playlist_number = 0
    current_playlist = []
    shuffle = True
    def query_list(self, list_of_choice):
        new_list = list_of_choice.replace(" ", "_")
        big_ol_list = []
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(new_list)
        mex = cur1.execute("SELECT Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid FROM {}".format(new_list))
        print(mex.description)
        #cur1.execute("SELECT Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid WHERE type='table' and name = ?", list_of_choice)
        #cur1.execute("SELECT Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid WHERE  name = ?", list_of_choice)
        rows = cur1.fetchall()
        for each in rows:
            imported_music = import_music(*each)
            big_ol_list.append(imported_music)
        print(f'Big_ol_list: {big_ol_list}')
        self.current_playlist = big_ol_list

    def initialized_song(self, song_link2):
        print(f'song_link2: {song_link2.Title} - {song_link2.Author}')
        global crossfade_ms
        crossfade_ms = 4000
        intialize_song = Path(song_link2.Savelocation) #.savelocation use in here not outside
        active_song = AudioSegment.from_file(intialize_song, format="mp4")
        return active_song

    def pydub_playsong(self, song_to_play):
        if self.inner_playing_loop is True:
            print(song_to_play.duration_seconds) #if was paused do self.playback = sleeptimer - pause_adjusttimer (paused now = true). else normal
            self.sleeptimer = song_to_play.duration_seconds #TODO change to less i think
            self.playback = pydub.playback._play_with_simpleaudio(song_to_play) #should probably be a loop of 1 second incremnt down with total amount
            print(f'right after assignment: {type(pydub.playback._play_with_simpleaudio(song_to_play))} and {self.playback.stop()}')
            time.sleep(self.sleeptimer) #TODO check if not playing then close thread? Threads linger after app closes..
            print("done playing rn")
            print(self.inner_playing_loop)

    def stop(self): #TODO this should also begin to kill the threads before they keep going. Essentially, music loop needs to have a check ccondition for if/when
        print(f'paused: {type(self.playback)}')
        self.playback.stop()
        print("clicked pause")
        self.inner_playing_loop = False
        print(f'playback.stop: {self.playback} is type: {type(self.playback)}')

    def testsong(self):
        sung = AudioSegment.from_file("F:\Files at random\MUSICAL\Downloads\Madvillain - Fancy ClownDgyMuIom9ys.mp3")
        pydub.playback._play_with_simpleaudio(sung)

    # play_loop needs to also take in a time based on the last pause. (like 16 seconds) to begin at said time
    def play_loop(self):
        # if shuffle is true, shuffle the music. pretty simple tbhh
        if self.shuffle is True:
            random.shuffle(self.current_playlist)
        try:
            # Not sure if this is exactly needed. but i like it here :D
            while self.inner_playing_loop is True:
                print("begin of looperoni!")
                print(f"self.playlist_number (begin) : {self.playlist_number}")
                current_song = self.initialized_song(self.current_playlist[self.playlist_number])
                thread_one = threading.Thread(target=self.pydub_playsong, args=(current_song,))
                thread_one.start()
                self.playlist_number = self.playlist_number + 1
                print(f"self.playlist_number (end) : {self.playlist_number}")
                thread_one.join()
                print("end of loop!")
        except IndexError:
            self.playlist_number = 0
            #self.play_loop()


    def skip_forward(self):
        print("clicked skip_forward")
        self.playback.stop()
        self.playlist_number = self.playlist_number + 1
        self.play_loop()


    def skip_backwards(self):
        pass
everyones_music = music_player()
#Initialized
class tkinter_main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1000x750+125+100")
        self.resizable(False, False)
        self.configure(bg="#272c34")
        self.title("Punge Testing")
        self.iconbitmap("./punge icon.ico")
        self.option_add('*tearOff', FALSE)
        main_page_frame = tk.Frame(self)
        main_page_frame.pack(side="top", fill="both", expand=True)
        main_page_frame.grid_rowconfigure(0, weight=1)
        main_page_frame.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for each_frame in (Main_page, Currently_playing, Settings, Download, mp4_downloader, active_playlist):
            frame = each_frame(main_page_frame, self)
            self.frames[each_frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Main_page)
    def show_frame(self, cont):
        frame = self.frames[cont]
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
        button_current.place(x=0,y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0,y=200)
        button_refresh = Button(self, text='Refresh', command=self.refresh_query)
        button_refresh.place(x=585,y=10)
        button_mp4.place(x=0, y=225)
        button_make_main_table = Button(self, text="TRY NEW PLAYLIST", command=self.create_new_table)
        button_make_main_table.place(relx=.5, rely=.6)

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
        popup_rename_window.title("Rename :D")
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


#TODO reformat all (query) things to look for <tkinter selected table> in database -> ./all_playlists.sqlite.
#TODO also need create_all_playlists to run only one time, or a "run if: not exists clause
#TODO primary key should be title. the <play> functions should also inherit from selected playlist.

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
                print(f'row: {super_row}')

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

    def popup_add_playlist(self):
        print("POPUP ADD PLAYLIST")
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



        # TODO 132 does not fetch requested ID of <selected> item. make it.

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
        everyones_music.inner_playing_loop = True
        print(f'playlist?: {playlist}')
        thren = threading.Thread(target=self.playmusic, args=playlist)
        thren.start()

    def playmusic(self, playlist_in):
        everyones_music.query_list(playlist_in)
        everyones_music.play_loop()

    def play_playlist(self, xia):
        certain_playlist = self.test1.selection()
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
                    playlist_table.insert('', tk.END, values=row)
                con1.close()
            #instance of music(begin_loop)



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



        def play_music_multithread():
            everyones_music.inner_playing_loop = True
            music_thread = threading.Thread(target=play_music)
            music_thread.start()

        def play_music():
            everyones_music.play_loop()

        play_button = ttk.Button(self, text="Play", command=play_music_multithread) #added args of selected playlist
        play_button.place(relx=.5, rely=.8)

        pause_button = ttk.Button(self, text="Pause bruh", command=everyones_music.stop)
        pause_button.place(relx=.5, rely=.75)

        slider = ttk.Scale(self, from_=0.01, to=0.2, orient="horizontal", command=volume_slider_controller)
        slider.place(rely=.5, relx=.5)

        mute_button = ttk.Button(self, text="mute", command=volume_mute)
        mute_button.place(rely=.5, relx=.65)

        skip_button = ttk.Button(self, text="Skip LOL", command=everyones_music.skip_forward)
        skip_button.place(rely=.3, relx=.5)

        stop_button = ttk.Button(self, text="stop", command=everyones_music.stop)
        stop_button.place(rely=.65, relx=.75)

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
        button_current.place(x=0,y=150)
        button_download.place(x=0, y=175)
        button_settings.place(x=0,y=200)
        button_mp4.place(x=0, y=225)

        # -----Listism-----#
        elite_fileloc = "F:/Files at random/MUSICAL/Downloads/"  # These will be detirmined by user eventualy
        elite_fileloc_thumbnail = "F:/Files at random/MUSICAL/thumbnails/"
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
                video_sep2 = video_main.streams.get_audio_only()
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
                              video_main.video_id, video_main.description)  # This should be, and IS NOT equal to the output file .mp3

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
        #self.bind("<<ShowFrame>>", self.query_all)


        playlist_title = ttk.Label(self, textvariable=global_playlist, anchor="center", background='#272c34', font=('Arial', 40))
        playlist_title.place(y=15, relx=.5)

        playlist_frame = Frame(self)
        playlist_frame.place(x=185, y=100)
        playlist_scroll = Scrollbar(playlist_frame)
        playlist_scroll.pack(side=RIGHT, fill=Y)

        style = ttk.Style()
        style.configure("mystyle.Treeview", font=('Calibri', 11), foreground='white', background='#262626')
        style.configure("mystyle.Treeview.Heading", font=('Times New Roman', 15), foreground='#262626', bg='blue')
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        global playlist_table
        playlist_table = ttk.Treeview(playlist_frame, yscrollcommand=playlist_scroll.set, xscrollcommand=playlist_scroll.set,
                             style="mystyle.Treeview", height=20)
        style.map('Treeview', background=[('selected', '#3f5e91')])
        playlist_scroll.config(command=playlist_table.yview)  # ability to scroll down

        playlist_table['columns'] = ('Artist', 'Song', 'Album')
        playlist_table.column("#0", width=0, stretch=NO)
        playlist_table.column('Artist', anchor=CENTER, width=250, stretch=NO)
        playlist_table.column('Song', anchor=CENTER, width=250, stretch=NO)
        playlist_table.column('Album', anchor=CENTER, width=250, stretch=NO)
        playlist_table.heading("#0", text='', anchor=CENTER)
        playlist_table.heading('Artist', text="Artist", anchor=CENTER)
        playlist_table.heading('Song', text="Song", anchor=CENTER)
        playlist_table.heading('Album', text='Album', anchor=CENTER)
        playlist_table.pack(expand=True, ipady="75")

    def query_all(self, event):
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        print(f'gbl playlist: (query_all): {global_playlist.get()}')
        cur1.execute("SELECT Author, Title, Album, Savelocation, SavelocationThumb, Uniqueid FROM {}".format(
            global_playlist.get()))
        # from 'main' need to inherit from a selelection from mainpage that includes a playlistname
        rows = cur1.fetchall()
        for row in rows:
            playlist_table.insert('', tk.END, values=row)
        con1.close()
        def query_all_playlists():
            con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
            cur1 = con1.cursor()
            cur1.execute("SELECT name FROM sqlite_master WHERE type='table';")
            rows = cur1.fetchall()
            return rows

        def add_to_playlist(playlist): #*kwargs should be music objects
            print(f'passed in playlist: {playlist}, play[0]={playlist[0]}')
            con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
            cur1 = con1.cursor()
            selected_songs = playlist_table.selection()
            print(playlist)
            for item in selected_songs:
                song_broken_down = playlist_table.item(item, 'values')
                print(f'title?: {song_broken_down[0]}, author:{song_broken_down[1]}, saveloc:{song_broken_down[2]}, thumbnail:{song_broken_down[3]}, album:{song_broken_down[4]}, id:{song_broken_down[5]}')
                print(f'song_suple: {item}')

                #print(f'selected_songs: {selected_songs}')
                #song_tuple = playlist_table.item(selected_songs, 'values')
                cur1.execute("INSERT INTO {} VALUES (?,?,?,?,?,?)".format(playlist[0]), (song_broken_down[1], song_broken_down[0], song_broken_down[3], song_broken_down[4], song_broken_down[2], song_broken_down[5]))
            con1.commit()


        def un_query_all():
            playlist_table.delete(*playlist_table.get_children())

        def delete_multiple(): #Deleting should exist in a 'deleting mode', should change the background color of TREEVIEW
            selection_items = playlist_table.selection()
            for item in selection_items:
                multiple_id = (playlist_table.item(item)['values'])
                remove_id = multiple_id[5]
                delete_from_db(remove_id, multiple_id[1])
                playlist_table.delete(item)
                os.remove(multiple_id[3])
                os.remove(multiple_id[4])

        def delete_from_db(id, song_named):
            connect1 = sqlite3.connect('MAINPLAYLIST.sqlite')
            concur2 = connect1.cursor()
            print(f'deleting: {song_named}')
            concur2.execute("DELETE FROM main WHERE Uniqueid=?", (id,))
            connect1.commit()
            concur2.close()


        def popup_event(event):
            try:
                song_menu.tk_popup(event.x_root, event.y_root)
            finally:
                song_menu.grab_release()

        def popup_rename(event):
            popup_rename_window = Toplevel(self)
            popup_rename_window.geometry("250x250+125+235") #TODO styling to not look terrible lol
            popup_rename_window.title("Rename :D")
            selected = playlist_table.focus()
            selected_song = playlist_table.item(selected, 'values')
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
                playlist_table.item(selected, text="",
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
            # TODO 132 does not fetch requested ID of <selected> item. make it.

        def popup_rename_multiple(event):
            popup_rename_multiple_window = Toplevel(self)
            popup_rename_multiple_window.geometry("250x250+125+235")
            popup_rename_multiple_window.title("Rename Multiple :D")
            all_selected = playlist_table.selection()
            for one_song in all_selected:
                selected_song = playlist_table.item(one_song, 'values')
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
                all_selected = playlist_table.selection()
                for one_song in all_selected:
                    selected_song = playlist_table.item(one_song, 'values')
                    print(f'selcted: {all_selected}')
                    print(f'selected_song: {selected_song}')
                    playlist_table.item(one_song, text='', values=(new_author, selected_song[1], new_album, selected_song[3], selected_song[4], selected_song[5]))
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

        song_menu = Menu(playlist_table, tearoff=0)


        playlist_submenu = Menu(song_menu)
        for playlist_name in query_all_playlists(): #inherits last one. all 1 command. want seperate if access quer() with [0]. iterator!
            playlist_submenu.add_command(label=playlist_name, command=lambda playlist_name=playlist_name: add_to_playlist(playlist_name))




        song_menu.add_cascade(label="Add To:", menu=playlist_submenu)
        song_menu.add_command(label="Rename", command=lambda: popup_rename("x"))
        song_menu.add_command(label="Delete", command=delete_multiple)
        song_menu.add_command(label="Rename Multiple", command=lambda: popup_rename_multiple("x"))
        playlist_table.bind("<Button-3>", popup_event)
        playlist_table.bind("<Delete>", lambda e: delete_multiple())

        def re_query_all():
            un_query_all()
            self.query_all("event")
            print("requireed!")


        button_refresh = Button(self, text='Refresh', command=re_query_all)
        button_refresh.place(x=10, y=10)

        re_query_all()


class AudioController:
    def __init__(self, process_name):
        self.process_name = process_name
        self.volume = self.process_volume()

    def process_volume(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                #print("Volume:", interface.GetMasterVolume())  # debug
                return interface.GetMasterVolume()

    def set_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # only set volume in the range 0.0 to 1.0
                self.volume = min(1.0, max(0.0, decibels))
                interface.SetMasterVolume(self.volume, None)
                #print("Volume set to", self.volume)  # debug
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





main_app = tkinter_main()
main_app.mainloop()
