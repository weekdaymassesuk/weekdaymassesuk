import os, sys
import win32com.client

conn = win32com.client.gencache.EnsureDispatch ("ADODB.Connection")
catalog = win32com.client.gencache.EnsureDispatch ("ADOX.Catalog")

TYPES = {
  win32com.client.constants.adArray : "Array",
  win32com.client.constants.adBigInt : "BigInt",
  win32com.client.constants.adBinary : "Binary",
  win32com.client.constants.adBoolean : "Boolean",
  win32com.client.constants.adBSTR : "BSTR",
  win32com.client.constants.adChapter : "Chapter",
  win32com.client.constants.adChar : "Char",
  win32com.client.constants.adCurrency : "Currency",
  win32com.client.constants.adDate : "Date",
  win32com.client.constants.adDBDate : "DBDate",
  win32com.client.constants.adDBTime : "DBTime",
  win32com.client.constants.adDBTimeStamp : "DBTimeStamp",
  win32com.client.constants.adDecimal : "Decimal",
  win32com.client.constants.adDouble : "Double",
  win32com.client.constants.adEmpty : "Empty",
  win32com.client.constants.adError : "Error",
  win32com.client.constants.adFileTime : "FileTime",
  win32com.client.constants.adGUID : "GUID",
  win32com.client.constants.adIDispatch : "IDispatch",
  win32com.client.constants.adInteger : "Integer",
  win32com.client.constants.adIUnknown : "IUnknown",
  win32com.client.constants.adLongVarBinary : "LongVarBinary",
  win32com.client.constants.adLongVarChar : "LongVarChar",
  win32com.client.constants.adLongVarWChar : "LongVarWChar",
  win32com.client.constants.adNumeric : "Numeric",
  win32com.client.constants.adPropVariant : "PropVariant",
  win32com.client.constants.adSingle : "Single",
  win32com.client.constants.adSmallInt : "SmallInt",
  win32com.client.constants.adTinyInt : "TinyInt",
  win32com.client.constants.adUnsignedBigInt : "UnsignedBigInt",
  win32com.client.constants.adUnsignedInt : "UnsignedInt",
  win32com.client.constants.adUnsignedSmallInt : "UnsignedSmallInt",
  win32com.client.constants.adUnsignedTinyInt : "UnsignedTinyInt",
  win32com.client.constants.adUserDefined : "UserDefined",
  win32com.client.constants.adVarBinary : "VarBinary",
  win32com.client.constants.adVarChar : "VarChar",
  win32com.client.constants.adVariant : "Variant",
  win32com.client.constants.adVarNumeric : "VarNumeric",
  win32com.client.constants.adVarWChar : "VarWChar",
  win32com.client.constants.adWChar : "WChar"
}

def main (mdb_filepath="masses.mdb"):
  conn.Open ("Provider=Microsoft.Jet.OLEDB.4.0;Data Source=%s;User Id=admin;Password=;" % mdb_filepath)
  catalog.ActiveConnection = conn

  for table in catalog.Tables:
    if table.Type in ('ACCESS TABLE', 'SYSTEM TABLE'): continue
    print
    print table.Name, "-", table.Type

    try:
      for column in table.Columns:
        print "  ", column.Name, TYPES[column.Type].upper ()
    except:
      print "   <Can't get columns>"

if __name__ == '__main__':
  main (*sys.argv[1:])
