import os, sys
from lxml import etree

import areas
import churches
import masses

def subgroup (obj, name, items):
  r = etree.Element (name)
  for item in items:
    value = getattr (obj, item, None)
    if value:
      etree.SubElement (r, item).text = unicode (value)
  return r

def area_as_xml (area_id):

  #
  # Find the area row from its id
  #
  area = areas.area (id=area_id)
  print area.name

  #
  # Add simple attributes if they exist
  #
  root = etree.Element ("area", id=unicode (area.id), code=area.code, name=area.name)
  for attr in ["details", "is_external"]:
    value = getattr (area, attr, None)
    if value:
      etree.SubElement (root, attr).text = unicode (value)

  #
  # Generate websites and add if there are any
  #
  websites = subgroup (
    area,
    "websites",
    ["%s_website" % w for w in "weekday sunday saturday holy_day_of_obligation".split ()]
  )
  if len (websites):
    root.append (websites)

  #
  # Generate coords and add if there are any
  #
  coords = subgroup (area, "coords", "latitude longitude zoom".split ())
  if len (coords):
    root.append (coords)

  #
  # Recurse for child areas
  #
  for area_id in areas.areas_in_immediate (area.id):
    root.append (area_as_xml (area_id))

  return root

def church_as_xml (church_id):

  def masstimes_as_xml (church, day_code, day_name):
    r = etree.Element (day_name)
    alt_text = getattr (church, "%s_mass_times" % day_name)
    if alt_text:
      etree.SubElement (r, "alt_text").text = unicode (alt_text)
    for row in masses.masses_by_church ([church_id], day_code):
      etree.SubElement (r, "time", hh24=row.hh24, eve=unicode (row.eve), restrictions=row.restrictions)
    return r

  church = churches.church (id=church_id)
  print churches.church_name (church)
  root = etree.Element ("church", id=unicode (church.id), name=church.name or "", alias=church.alias or "")

  #
  # Add static elements
  #
  for item in [
    'is_parish', 'is_shrine', 'is_external',
    'address', 'postcode', 'phone', 'email',
    'public_transport', 'directions',
    'last_updated_on'
  ]:
    value = getattr (church, item, None)
    if value:
      etree.SubElement (root, item).text = unicode (value)

  coords = subgroup (church, "coords", "latitude longitude scale".split ())

  #
  # Find all the areas the church is in
  #
  church_areas = etree.SubElement (root, "areas")
  for area_id in churches.church_areas (church_id):
    etree.SubElement (church_areas, "area").text = areas.area (id=area_id).name

  masstimes = etree.SubElement (root, "masstimes")
  for code, name in [("k", "weekday"), ("u", "sunday"), ("a", "saturday"), ("h", "holy_day_of_obligation")]:
    masstimes.append (masstimes_as_xml (church, code.upper (), name.lower ()))
  return root

def main ():
  root = etree.Element ("weekdaymasses.org.uk")

  print "Areas:"
  all_areas = etree.SubElement (root, "areas")
  scotland = areas.area (code="scotland")
  all_areas.append (area_as_xml (scotland.id))
  print

  print "Churches:"
  all_churches = etree.SubElement (root, "churches")
  for church_id in areas.all_churches_in (scotland.id):
    all_churches.append (church_as_xml (church_id))
  print

  with open ("weekdaymasses.xml", "w") as f:
    f.write (etree.tostring (root, pretty_print=True))
  os.startfile ("weekdaymasses.xml")

if __name__ == '__main__':
  main (*sys.argv[1:])
