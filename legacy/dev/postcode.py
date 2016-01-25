import config
import database
import utils

"""
GB Postcodes are of the general form: A[A][9]9[A] 9AA.
  We are concerned only with the first "word", ie the sequence preceding the space
While most towns use a mnemonic of the city for the opening letters (B for Bristol,
  CR for Croydon, etc.), London postcodes form a special class, using points of the compass
  within London. Legitimate examples (all within London) include: SW6, SE20, N11, W5, SW1H.
They should order as follows:
  London postcodes precede all others, internally ordered as follows:
    N, E, EC, SE, SW, W, WC, NW
    numbers in numeric and not alphabetic order (ie SE2 precedes SE10)
    letter suffixes come last within their number group (ie SW1 precedes SW1H)
  All other postcodes are ordered by:
    letter prefix (ie BS6 precedes CR0)
    number suffix in numeric and not alphabetic order (ie RG2 precedes RG10)
"""
def split_postcode (postcode_text):
  import re

  #
  # Split into space-separated parts, adding a blank
  #  sentinel in case no second part is supplied.
  #
  postcode = postcode_text.upper ().split () + [""]

  #
  # Distinguish the different parts (cf explanation above)
  # This regular expression guarantees exactly 3 groups,
  #  even if the postcode has fewer parts (or erroneously
  #  has more).
  #
  postcode_re = re.compile ("([A-Z]+)([0-9]+)([A-Z]*)")
  m = postcode_re.match (postcode[0])
  if m:
    (letters, numbers, residue) = m.groups ()
    round = postcode[1]
  else:
    (letters, numbers, residue) = ("", 0, "")
    round = postcode_text
  return (letters, int (numbers), residue, round)

class Postcode:

  def __init__ (self, postcode_text):
    self.postcode_text = postcode_text
    self.components = self.split ()

  def split (self):
    return self.postcode_text.split ()

  def __repr__ (self):
    return "<Postcode %s>" % self.postcode_text

  def __str__ (self):
    return "<Postcode %s>" % " ".join (self.components)

  def __cmp__ (self, other):
    #
    # Python's boolean short-circuiting will make sure
    #  that if either object is false to start with, no
    #  attempt will be made to normalise it. Since both
    #  comparison targets must be postcode objects, the
    #  only false value is None.
    #
    return cmp (self and self.normalised (), other and other.normalised ())

  def __nonzero__ (self):
    return len (self.postcode_text)

  def is_valid (self):
    return bool (len (self.postcode_text))

  def prefix (self):
    return (self.components + [""])[0]

  def suffix (self):
    return (self.components + [""])[1]

  def order (self):
    return None

  def normalised (self):
    """
    """
    return (self.order (), self.components)

  def coords (self):
    for row in database.select ("SELECT os_x, os_y FROM postcode_coords WHERE outcode = ?", [self.prefix ()]):
      return row.os_x, row.os_y

class Postcode_GB (Postcode):

  LONDON_POSTCODES = {
    "N" : 1, "E" : 2, "EC" : 3, "SE" : 4,
    "SW" : 5, "W" : 6, "WC" : 7, "NW" : 8
  }

  def __init__ (self, postcode_text, london_is_special=True):
    Postcode.__init__ (self, postcode_text)
    (self.letters, self.numbers, self.residue, self.round) = self.components
    self.london_is_special = london_is_special

  def prefix (self):
    return self.letters + str (self.numbers)

  def suffix (self):
    return self.residue

  def split (self):
    return split_postcode (self.postcode_text)

  def is_valid (self):
    return self.letters > ''

  def order (self):
    #
    # If postcode is in London, prepend an artificial order key
    #
    if self.london_is_special:
      return self.LONDON_POSTCODES.get (self.letters, 99)
    else:
      return None

  def in_london (self):
    if self.london_is_special:
      return self.LONDON_POSTCODES.has_key (self.letters)
    else:
      return False

postcode = Postcode_GB

def postcode_areas ():
  "Return a distinct list of the areas which have postcode coordinates"
  SELECT_SQL = u"""
    SELECT DISTINCT
      a.code AS code,
      a.name AS name
    FROM
      postcode_coords AS pco
    JOIN areas AS a ON
      a.id = pco.area_id
  """
  for row in database.select (SELECT_SQL):
    yield row.code, row.name
