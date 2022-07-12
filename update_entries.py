
import sqlite3


def change_entries():
    con = sqlite3.connect("F:/Projects/Python Projects/punge/MAINPLAYLIST.sqlite")
    cur = con.cursor()
    redo_list = []
    row = cur.execute("SELECT Savelocation, SavelocationThumb, Uniqueid FROM main")
    for item in row:
        y = (change_part(item[0]))
        x = (change_part(item[1]))
        z = item[2]
        return_tuple = (y, x, z)
        redo_list.append(return_tuple)
    update_db(redo_list)


def update_db(in_list):
    con = sqlite3.connect("F:/Projects/Python Projects/punge/MAINPLAYLIST.sqlite")
    cur = con.cursor()
    for intuple in in_list:
        cur.execute("UPDATE main Set Savelocation=? , SavelocationThumb=? WHERE Uniqueid=?", (intuple[0], intuple[1], intuple[2]))
        con.commit()
    print("Success !")





def change_part(sample):
    removed = sample[26:]
    new_part = "F:/Punge Downloads"
    super_new = new_part + removed
    return super_new

change_entries()
