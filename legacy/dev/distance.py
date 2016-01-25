from decimal import Decimal

class Distance (object):
  
  conversion = {
    "METRES" : Decimal ("1.0"),
    "MILES" : Decimal ("1609.0"),
    "KM" : Decimal ("1000.0")
  }
  
  def __init__ (self, distance, units="METRES"):
    self.metres = distance * self.conversion[units]

  def as_ (self, units="METRES"):
    return self.metres / self.conversion[units]

  def as_metres (self):
    return self.as_ (units="METRES")

  def as_miles (self):
    return self.as_ (units="MILES")
  
  def as_km (self):
    return self.as_ (units="KM")
