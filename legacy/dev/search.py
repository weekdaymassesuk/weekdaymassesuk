import config
import areas
import database

SEARCH_SQL = u"""
  SELECT
    church_id,
    word,
    score
  FROM
    search_scores
  WHERE
    word IN (%s)
"""
def find_churches (area_code, terms, all_or_some="ANY"):
  area = areas.area (code=area_code or config.ROOT_AREA_CODE)
  churches = set (areas.all_churches_in (area.id))
  n_terms = len (terms)

  results = {}
  for row in database.select (SEARCH_SQL % u", ".join ("'%s'" % t for t in terms)):
    if row.church_id not in churches:
      continue
    else:
      results.setdefault (row.church_id, []).append (row.score)

  hits = ((sum (scores), len (scores), church_id) for church_id, scores in results.items () if (all_or_some == "SOME" or len (scores) == n_terms))
  return [church_id for score, scores, church_id in sorted (hits, reverse=True)]
