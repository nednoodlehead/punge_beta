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

#Initialized
class tkinter_main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("750x500+125+225")
        self.configure(bg="#272c34")
        self.title("Punge Testing")
        self.iconbitmap("./punge icon.ico")
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

class Main_page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#272c34")
        playlist_frame = Frame(self)
        playlist_frame.place(x=185, y=100)
        playlist_scroll = Scrollbar(playlist_frame)
        playlist_scroll.pack(side=RIGHT, fill=Y)

        style = ttk.Style()
        style.configure("mystyle.Treeview", font=('Calibri', 11), foreground='white', background='#262626')
        style.configure("mystyle.Treeview.Heading", font=('Times New Roman', 15), foreground='#262626', bg='blue')
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        test1 = ttk.Treeview(playlist_frame, yscrollcommand=playlist_scroll.set, xscrollcommand=playlist_scroll.set, style="mystyle.Treeview")
        style.map('Treeview', background=[('selected', '#3f5e91')])
        playlist_scroll.config(command=test1.yview)  # ability to scroll down

        test1['columns'] = ('Image', 'Title', 'Description')
        test1.column("#0", width=0, stretch=NO)
        test1.column('Image', anchor=CENTER, width=100)
        test1.column('Title', anchor=CENTER, width=225)
        test1.column('Description', anchor=CENTER, width=250)
        test1.heading("#0", text='', anchor=CENTER)
        test1.heading('Image', text="Image", anchor=CENTER) #Remove this & 2 below after. exists for debugging purposes
        test1.heading('Title', text="Title", anchor=CENTER)
        test1.heading('Description', text='Description', anchor=CENTER)
        test1.pack(expand=True, ipady="75")
        #Needs to be here cause of reefernce b4 all other functions


        def create_new_table():
            popup_rename_window = Toplevel(self)
            popup_rename_window.geometry("250x250+125+235")
            popup_rename_window.title("Rename :D")
            new_playlist_name = StringVar()
            playlist_entry = Entry(popup_rename_window, textvariable=new_playlist_name)
            playlist_entry.place(relx=.5, rely=.75)
            playlist_create = Button(popup_rename_window, text="Create!!", command=lambda: create_playlist_combine(playlist_entry.get()))
            playlist_create.place(rely=.5, relx=.5)

            def create_playlist_combine(play_enter):
                table_backend(play_enter)
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

        def refresh_query():
            un_query_all()
            query_all()
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
        button_refresh = Button(self, text='Refresh', command=refresh_query)
        button_refresh.place(x=585,y=10)
        button_mp4.place(x=0, y=225)
        button_make_main_table = Button(self, text="TRY NEW PLAYLIST", command=create_new_table)
        button_make_main_table.place(relx=.5, rely=.6)

        def query_all():
            con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
            cur1 = con1.cursor()
            cur1.execute("SELECT name FROM sqlite_master WHERE type='table';")
            rows = cur1.fetchall()
            for row in rows:
              test1.insert('', tk.END, values=row) #fixed
            con1.close()

        def un_query_all():
            test1.delete(*test1.get_children())


        def change_options(): #Deleting should exist in a 'deleting mode', should change the background color of TREEVIEW
            selection_playlist = test1.selection()
            print(selection_playlist)

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

        def popup_add_playlist():
            print("POPUP ADD PLAYLIST")
        def popup_rename(event):
            popup_rename_window = Toplevel(self)
            popup_rename_window.geometry("250x250+125+235") #TODO styling to not look dogshit lol
            popup_rename_window.title("Rename :D")
            selected = test1.focus()
            selected_song = test1.item(selected, 'values')
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
                test1.item(selected, text="",
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
            all_selected = test1.selection()
            for one_song in all_selected:
                selected_song = test1.item(one_song, 'values')
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
                all_selected = test1.selection()
                for one_song in all_selected:
                    selected_song = test1.item(one_song, 'values')
                    print(f'selcted: {all_selected}')
                    print(f'selected_song: {selected_song}')
                    test1.item(one_song, text='', values=(new_author, selected_song[1], new_album, selected_song[3], selected_song[4], selected_song[5]))
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
                    "UPDATE main SET Author=?, Title=?, Album=? , Savelocation=?, SavelocationThumb=? WHERE Uniqueid=?",
                    (update_author, retain_title, update_album, retain_download_mp3, retain_download_jpg, retain_song_id,))

                connect1.commit()
                connect1.close()
            popup_rename_multiple_window.bind("<Return>", rename_multiple_destory_combine)

        song_menu = Menu(test1, tearoff=0)
        song_menu.add_command(label="Add To:", command=popup_add_playlist)
        song_menu.add_command(label="Rename", command=lambda: popup_rename("x"))
        song_menu.add_command(label="Edit Name", command=change_options)
        song_menu.add_command(label="Rename Multiple", command=lambda: popup_rename_multiple("x"))
        test1.bind("<Button-3>", popup_event)
        test1.bind("<Delete>", lambda e: change_options)
        #self.bind("<Return>", bind_test)
        #self.entry1.delete(0, 'end)
        query_all()

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
        instance_of_music = music_player()

        #I hate images in tkinter
        #    path1 = Image.open("F:/Files at random/MUSICAL/thumbnails/Death Grips - HackeruoZgZT4DGSY.jpg")
        #    opened_thumb = ImageTk.PhotoImage(path1)
        #    mei = Label(self, image=opened_thumb)
        #    mei.place(x=200, y=200)



        def play_music_multithread():
            music_thread = threading.Thread(target=play_music)
            music_thread.start()

        def play_music(): #take playlist eventually? also random.shuffle should inherit from whether or not the button is toggled
            import_funnies = instance_of_music.query_list()
            random.shuffle(import_funnies)
            instance_of_music.main_music_loop_entry(import_funnies)
        play_button = ttk.Button(self, text="Play", command=play_music_multithread)
        play_button.place(relx=.5, rely=.8)

        pause_button = ttk.Button(self, text="Pause bruh", command=instance_of_music.pause)
        pause_button.place(relx=.5, rely=.75)

        slider = ttk.Scale(self, from_=0.01, to=0.2, orient="horizontal", command=volume_slider_controller)
        slider.place(rely=.5, relx=.5)

        mute_button = ttk.Button(self, text="mute", command=volume_mute)
        mute_button.place(rely=.5, relx=.65)

        skip_button = ttk.Button(self, text="Skip LOL", command=instance_of_music.skip_forward)
        skip_button.place(rely=.3, relx=.5)

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
            #TODO fix complication with ^ .get(). it wants "self", but then the other thing gets pissy if it has argument
            #TODO maybe exclude it somehow? some sort of designation? take to new tab and try to isolate problem
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

        def add_to_db(vid_auth, vid_titl, vid_id, vid_desc): #TODO MP3 and Jpg extensions need to include the vid_id to be exempt from a mass name failiure?
            part1_db = difference_author_title(vid_auth, vid_titl)[0] #TODO it is partially done, will need to do a re-do of all existing file maybe. Perhaps the import should stay unimpacted, as passed in object
            part2_db = difference_author_title(vid_auth, vid_titl)[1] #TODO will be the path with id in it.
            part3_db = file_extension_change_mp3(vid_auth, vid_titl, vid_id)
            part4_db = file_extension_change_jpg(vid_auth, vid_titl, vid_id)
            part5_db = album_check(vid_desc)
            part6_db = vid_id

            class_object = db.import_info123(part1_db, part2_db, part3_db, part4_db, part5_db, part6_db)
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
            vid_download.download(output_path=pathism)




        def download_mp3_differ():
            pathism = desire_path.get()
            if os.path.exists(pathism) is False:
                print("Fucking dumbass choose a proper path")
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
                print("stupid dumbass")
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

class music_player:
    current_playing1 = 3
    current_playing2 = 2


    def query_list(self):
        big_ol_list = []
        con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
        cur1 = con1.cursor()
        cur1.execute("SELECT Title, Author, Album, SavelocationThumb, Savelocation, Uniqueid FROM main")
        rows = cur1.fetchall()
        for each in rows:
            imported_music = import_music(*each)
            big_ol_list.append(imported_music)
        print(f'Big_ol_list: {big_ol_list}')
        return big_ol_list

    def initialized_song(self, song_link2):
        print(f'song_link2: {song_link2.Title} - {song_link2.Author}') #Reversed for no good reason?
        global crossfade_ms
        crossfade_ms = 10000
        intialize_song = Path(song_link2.Savelocation) #.savelocation use in here not outside
        active_song = AudioSegment.from_file(intialize_song, format="mp4")
        songpt1 = active_song[:crossfade_ms]
        songpt2 = active_song[crossfade_ms:-crossfade_ms]
        songpt3 = active_song[-crossfade_ms:]
        return songpt1, songpt2, songpt3

    def pydub_playsong(self, song_to_play):
        print(song_to_play.duration_seconds)
        #time.sleep(timeism_1)
        #play(song_to_play)

        #time.sleep(len(song_to_play))
        pydub.playback._play_with_simpleaudio(song_to_play)
        time.sleep(song_to_play.duration_seconds)
        print("done playing rn")


    def main_music_loop(self, song_list, thread_one, song_one):
        global inner_playing_loop
        inner_playing_loop = True
        while inner_playing_loop is True:
            try:
                print("Thread begins")
                thread_one.start()
                print("Initializing song...")
                song_two = self.initialized_song(song_list[self.current_playing2])
                crossfade_1 = song_one[2].append(song_two[0], crossfade=crossfade_ms)
                self.current_playing2 = self.current_playing2 + 2
                thread_two = threading.Thread(target=self.pydub_playsong, args=(song_two[
                                                                               1],))  # threading just to initialize everything during the first bit. would want to change to [1] to give most time possible to init
                thread_one.join()

                # TODO wrao more code in thread.start -> thread.join() methods to increase efficiency. perhaps update loop prelude

                play(crossfade_1)
                thread_two.start()
                print("making crossfade")
                self.current_playing1 = self.current_playing1 + 2  # makes it 3
                song_one = self.initialized_song(song_list[self.current_playing1])  # makes it 1
                crossfade_2 = song_two[2].append(song_one[0], crossfade=crossfade_ms)
                thread_one = threading.Thread(target=self.pydub_playsong, args=(song_one[1],))
                thread_two.join()
                play(crossfade_2)
                print("Loop time")
            except IndentationError:
                print("INDEX RAISED. REPEAT TIME")
                end_init = self.initialized_song(song_list[-1])
                start_init = self.initialized_song(song_list[0])
                combine_restart = end_init[2].append(start_init[0], crossfade=crossfade_ms)
                play(combine_restart)
                self.current_playing = 0
                self.current_playing2 = 1
                continue
         #- should crossfade into song 3...?
    def main_music_loop_entry(self, song_list):
        entry_song = self.initialized_song(song_list[0])
        begin_thr = threading.Thread(target=self.pydub_playsong, args=(entry_song[0],))
        begin_thr.start()
        print("initialize song 2")
        entry_song_MT = threading.Thread(target=self.pydub_playsong, args=(entry_song[1],))
        begin_thr.join()
        entry_song_MT.start()
        song_one = self.initialized_song(song_list[1])
        entry_crossfade = entry_song[2].append(song_one[0], crossfade=crossfade_ms)
        thread_one = threading.Thread(target=self.pydub_playsong, args=(song_one[1],))
        entry_song_MT.join()
        ent_crsfade = threading.Thread(target=self.pydub_playsong, args=(entry_crossfade,))
        ent_crsfade.start()
        print("entering loop")
        ent_crsfade.join()
        self.main_music_loop(song_list, thread_one, song_one)

    def pause(self): #dont work
        pass


    def skip_forward(self):
        print(f' current1: {self.current_playing1}')
        print(f' current2: {self.current_playing2}')
        #Kill thread 1 & 2
        #mainmusic entry with new numbers


    def skip_backwards(self):
        pass

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

        playlist_frame = Frame(self)
        playlist_frame.place(x=185, y=100)
        playlist_scroll = Scrollbar(playlist_frame)
        playlist_scroll.pack(side=RIGHT, fill=Y)

        style = ttk.Style()
        style.configure("mystyle.Treeview", font=('Calibri', 11), foreground='white', background='#262626')
        style.configure("mystyle.Treeview.Heading", font=('Times New Roman', 15), foreground='#262626', bg='blue')
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        playlist_table = ttk.Treeview(playlist_frame, yscrollcommand=playlist_scroll.set, xscrollcommand=playlist_scroll.set,
                             style="mystyle.Treeview")
        style.map('Treeview', background=[('selected', '#3f5e91')])
        playlist_scroll.config(command=playlist_table.yview)  # ability to scroll down

        playlist_table['columns'] = ('Artist', 'Song', 'Album')
        playlist_table.column("#0", width=0, stretch=NO)
        playlist_table.column('Artist', anchor=CENTER, width=150)
        playlist_table.column('Song', anchor=CENTER, width=250)
        playlist_table.column('Album', anchor=CENTER, width=140)
        playlist_table.heading("#0", text='', anchor=CENTER)
        playlist_table.heading('Artist', text="Artist", anchor=CENTER)
        playlist_table.heading('Song', text="Song", anchor=CENTER)
        playlist_table.heading('Album', text='Album', anchor=CENTER)
        playlist_table.pack(expand=True, ipady="75")

        def query_all():
            con1 = sqlite3.connect("./MAINPLAYLIST.sqlite")
            cur1 = con1.cursor()
            cur1.execute("SELECT Author, Title, Album, Savelocation, SavelocationThumb, Uniqueid FROM main") #from 'main' need to inherit from a selelection from mainpage that includes a playlistname
            rows = cur1.fetchall()
            for row in rows:
                playlist_table.insert('', tk.END, values=row)
            con1.close()

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

        def popup_add_playlist():
            print("POPUP ADD PLAYLIST")
        def popup_rename(event):
            popup_rename_window = Toplevel(self)
            popup_rename_window.geometry("250x250+125+235") #TODO styling to not look dogshit lol
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
        song_menu.add_command(label="Add To:", command=popup_add_playlist)
        song_menu.add_command(label="Rename", command=lambda: popup_rename("x"))
        song_menu.add_command(label="Delete", command=delete_multiple)
        song_menu.add_command(label="Rename Multiple", command=lambda: popup_rename_multiple("x"))
        playlist_table.bind("<Button-3>", popup_event)
        playlist_table.bind("<Delete>", lambda e: delete_multiple())



        query_all()

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
