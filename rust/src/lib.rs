use pyo3::prelude::*;
use walkdir::WalkDir;
use rusqlite::*;
use std::fs;

const MP3PATH: &str = "F:/Punge Downloads/Downloads/";
const JPGPATH: &str = "F:/Punge Downloads/thumbnails/";
const DBPATH: &str = "F:/Projects/Python Projects/punge/MAINPLAYLIST.sqlite";

#[derive(Debug)]
#[derive(Clone)]
struct MusicDerived {
    mp3: String,
    jpg: String
}

fn get_db() -> Vec<MusicDerived> {
    let mut return_vec: Vec<MusicDerived> = Vec::new();
    let con = Connection::open(DBPATH).unwrap();
    let mut prep = con.prepare("SELECT Savelocation, SavelocationThumb FROM main").unwrap();
    let prep_iter = prep.query_map(params![], |row| {
        Ok(MusicDerived {
            mp3: row.get(0)?,
            jpg: row.get(1)?,
        })
    }).unwrap();
    for music_entry in prep_iter.into_iter() {
        let music_entry = music_entry.unwrap();
        return_vec.push(music_entry)
    }
    return return_vec
}


fn list_dir_contents(in_path: &str) -> Vec<String> {
    let nut = WalkDir::new(in_path).into_iter();
    let mut count: i32 = 0;
    let mut return_vec: Vec<String> = Vec::new();
    for x in nut {
        let x = x.unwrap().path().to_str().unwrap().to_string();
        return_vec.push(x);
        count += 1
    }
    // Compensate for first entry being the directory itsself
    println!("COUNT: {}", count - 1);
    return_vec.remove(0);
    return return_vec
}
#[pyfunction]
fn in_dir_not_db(py: Python<'_>) -> (PyObject, PyObject) {
    let mut return_vec_mp3: Vec<String> = Vec::new();
    let mut return_vec_jpg: Vec<String> = Vec::new();
    let db_contents = get_db();
    let dir_contents_mp3 = list_dir_contents(MP3PATH);
    let dir_contents_jpg= list_dir_contents(JPGPATH);
    let mut mp3_list: Vec<String> = Vec::new();
    let mut jpg_list: Vec<String> = Vec::new();

    for db_entry in db_contents {
        let MusicDerived {mp3, jpg} = db_entry;
        jpg_list.push(jpg);
        mp3_list.push(mp3);
    }
    for mp3_file in dir_contents_mp3 {
        if !mp3_list.contains(&mp3_file) {
            return_vec_mp3.push(mp3_file);
        }

    }
    //println!("mp3_list:: {:?}", &mp3_list);
    //println!("JPG_LIST:: {:?}", &jpg_list);

    for jpg_file in dir_contents_jpg {
        if !jpg_list.contains(&jpg_file) {
            return_vec_jpg.push(jpg_file);
        }
    }
    let return_vec_mp3 = return_vec_mp3.into_py(py);
    let return_vec_jpg = return_vec_jpg.into_py(py);

return (return_vec_mp3, return_vec_jpg)

}



#[pyfunction]
fn delete_all(in_vec_jpg: Vec<String>, in_vec_mp3: Vec<String> ) {
    for item in in_vec_jpg {
        fs::remove_file(&item).unwrap();
        println!("deleted: {}", &item)
    }
    for item in in_vec_mp3 {
        fs::remove_file(&item).unwrap();
        println!("deleted: {}", &item)
    }
}
/*
#[pyfunction]
fn print_it(one: String, two: String) -> String {
    let news = MusicDerived{mp3: one, jpg: two};
    return news.mp3
}
*/


#[pymodule]
fn data_clean(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(delete_all, m)?)?;
    m.add_function(wrap_pyfunction!(in_dir_not_db, m)?)?;
    Ok(())
}