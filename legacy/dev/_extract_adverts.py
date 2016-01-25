#!python2
import os, sys
import tempfile
import pyodbc

def main(mdb_filepath=r"data\masses.accdb"):
    dirpath = tempfile.mkdtemp()

    db = pyodbc.connect ("Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s;Uid=Admin;Pwd=;" % mdb_filepath)
    try:
        q = db.cursor()
        q.execute("SELECT * FROM Adverts")
        for id, organisation, filename, url, image, image_2 in q.fetchall():
            print id, organisation, filename, url
            filepath = os.path.join(dirpath, filename)
            with open(filepath, "wb") as f:
                f.write(image_2)
                print "  =>", filepath
    finally:
        db.close()

    os.startfile(dirpath)

if __name__ == '__main__':
    main(*sys.argv[1:])
