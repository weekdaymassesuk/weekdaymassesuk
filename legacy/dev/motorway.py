import re

MOTORWAY_PATTERN = "(A|M)(\d+)(\(M\))?"
JUNCTION_PATTERN = "(J|T)?(\d+)([A-Za-z])?"

class MJ (object):

  def __init__ (self, data):
    self.text = data
    if data is None:
      self.data = self.prefix = self.numbers = self.suffix = ""
    else:
      self.data = data.upper ().replace (" ", "")
      items = self.pattern.match (self.data).groups ()
      self.prefix = items[0] or self.defaults[0]
      self.numbers = int (items[1])
      self.suffix = items[2] or self.defaults[2]

  def __nonzero__ (self):
    return bool (self.data)

  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.text)

  def __str__ (self):
    return "%s%s%s" % (self.prefix, self.numbers, self.suffix)

  def __cmp__ (self, other):
    return cmp ((self.prefix, self.numbers, self.suffix), (other.prefix, other.numbers, other.suffix))

  def __hash__ (self):
    return hash ((self.prefix, self.numbers, self.suffix))

class Motorway (MJ):

  #
  # A motorway is an A or an M followed by 1 or more
  # digits, followed optionally by an M in brackets.
  #
  pattern = re.compile (MOTORWAY_PATTERN)
  defaults = ("M", None, "")
  prefix_order = ["M", "A"]

  def __init__ (self, data):
    MJ.__init__ (self, data)
    self.ordering = str (self.numbers), self.prefix_order.index (self.prefix), self.suffix
    self._junctions = None

  def __cmp__ (self, other):
    return cmp (self.ordering, other.ordering)

class Junction (MJ):

  #
  # A junction is a J or a T followed by one or
  # more letters with an optional letter suffix.
  #
  pattern = re.compile (JUNCTION_PATTERN)
  defaults = ("J", None, "")

  #
  # Junctions sort differently because of the T-junctions
  # on the M62 Toll.
  #
  def __cmp__ (self, other):
    return cmp ((self.numbers, self.prefix, self.suffix), (other.numbers, other.prefix, other.suffix))

