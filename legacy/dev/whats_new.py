from __future__ import generators

import config
import database
import utils

def latest_updates (n_updates=config.N_UPDATES):
  for update in database.select (u"SELECT * FROM whats_new ORDER BY updated_on DESC"):
    yield update

if __name__ == '__main__':
  pass
