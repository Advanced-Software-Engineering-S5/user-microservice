#!/usr/bin/env python

from user_microservice import create_app
import sys

dbfile = len(sys.argv) > 1 and sys.argv[1] or "userdb.db"

create_app(dbfile=dbfile).run(host="0.0.0.0")
