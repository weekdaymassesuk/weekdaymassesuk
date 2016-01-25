#!python2
import os, sys
import glob

import xlrd

import config
import database

def populate_translation (workbook, language):
    INSERT_SQL = """
    INSERT INTO
        translations
    (
        language,
        key,
        translation
    )
    VALUES
    (
        ?,
        ?,
        ?
    )
    """
    print language
    sheet = workbook.sheet_by_name (language)
    for n_row in range (sheet.nrows):
        values = [v for v in sheet.row_values (n_row, 0, 2) if v]
        if len (values) == 2:
            key, value = values
            database.execute (INSERT_SQL, [language, key.lower(), value])

def populate_urls (workbook):
    INSERT_URL_SQL = """
    INSERT INTO
        translation_urls
    (
        key,
        sequence,
        url
    )
    VALUES
    (
        ?,
        ?,
        ?
    )
    """
    url_sheet = workbook.sheet_by_name ("urls")
    for key, values in ((url_sheet.row_values (n)[0], url_sheet.row_values (n)[1:]) for n in range (url_sheet.nrows)):
        for n, value in enumerate (v for v in values if v):
            database.execute (INSERT_URL_SQL, [key, n, value])

def populate_translations ():
    populate_urls (xlrd.open_workbook ("data/translations/translations.urls.xls"))
    for sheet_name in glob.glob ("data/translations/translations.??.xls"):
        populate_translation (
            xlrd.open_workbook (sheet_name),
            os.path.basename (sheet_name).split (".")[1]
        )

def main (*args):
    database.execute ("DELETE FROM translations")
    database.execute ("DELETE FROM translation_urls")
    populate_translations ()
    database.db.commit ()

if __name__ == '__main__':
    main (sys.argv[1:])
    raw_input ("Press enter...")
