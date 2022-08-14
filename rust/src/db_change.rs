use rusqlite::*;
use pyo3::prelude::*;

pub struct MusicDerived {
    saveloc: String,
    savelocthumb: String,
    uniqueid: String
}
#[derive(Debug)]
pub struct Table {
    name: String
}

fn fix_saveloc_str(prefix: &str, loc: &str, loc_thumb: &str, file: &MusicDerived) -> (String, String) {
        let saveloc_iter = file.saveloc.split("/").collect::<Vec<&str>>();
        let saveloc_iter_thumb = file.savelocthumb.split("/").collect::<Vec<&str>>();
        let saveloc_index = saveloc_iter.len() - 1;
        let saveloc_name = saveloc_iter[saveloc_index];
        let new_name_loc = prefix.to_owned() + "/" + loc + "/" + &saveloc_name;
        let savelocthumb_index = saveloc_iter_thumb.len() - 1;
        let savelocthumb_name = saveloc_iter_thumb[savelocthumb_index];
        let new_name_thumb = prefix.to_owned()+ "/" + loc_thumb + "/" + &savelocthumb_name;
        return (new_name_loc, new_name_thumb)
}

pub fn query_all_playlist() -> Vec<String> {
    let mut return_vec: Vec<String> = Vec::new();
    let con = Connection::open("MAINPLAYLIST.sqlite").unwrap();
    let mut stmt = con.prepare("SELECT name FROM sqlite_master WHERE type='table';").unwrap();
    let iter = stmt.query_map(params![], |row| {
        Ok(Table {
        name: row.get(0)?,})
    }).unwrap();
         // .unwrap() after } needed?
    for item in iter.into_iter() {
        let item = item.unwrap();
        return_vec.push(item.name)
    }
    println!("Query all done!");
    return_vec
}



// 'replace all' assumes that the mp3 & jpg download location are two subdirs inside of a parent directory
// that parent directory is the first parameter, the directory name of mp3, jpg are second and third
// respectively
// replace_all_saveloc_prefix("F:/downloads/punge", "mp3 downloads", "jpg downloads");
#[pyfunction]
pub fn replace_all_saveloc_prefix(new_prefix: &str, mp3_loc: &str, jpg_loc: &str) {
    let table_iter = query_all_playlist();
    for entry in table_iter {
        change_saveloc_prefix(new_prefix, entry.as_str(), mp3_loc, jpg_loc);
        println!("{} completed!", &entry)
    }
}

pub fn change_saveloc_prefix(new_prefix: &str, playlist: &str, mp3_loc: &str, jpg_loc: &str) {
    let con = Connection::open("./MAINPLAYLIST.sqlite").unwrap();
    let mut sel = con.prepare(format!("SELECT Savelocation, SavelocationThumb, Uniqueid FROM {}", playlist).to_string().as_str()).unwrap();
    let derive_iter = sel.query_map(params![], |row| {
        Ok(MusicDerived {
            saveloc: row.get(0)?,
            savelocthumb: row.get(1)?,
            uniqueid: row.get(2)?
        })
    }).unwrap();
    for entry in derive_iter.into_iter() {
        let before = entry.unwrap();
        let new_saveloc_tuple = fix_saveloc_str(&new_prefix, &mp3_loc, &jpg_loc, &before);
        // should be iterated over for each playlist? or else playlists loose functionality
        let mut stmnt = con.prepare(
        format!("UPDATE {} SET Savelocation=?, SavelocationThumb=? where Uniqueid=?", playlist).as_str()).unwrap();
         stmnt.execute(&[ (new_saveloc_tuple.0.to_string().as_str()), (new_saveloc_tuple.1.to_string().as_str()
         ), (before.uniqueid.as_str())]).unwrap();
        println!("updated: {}", new_saveloc_tuple.0)

    }
}