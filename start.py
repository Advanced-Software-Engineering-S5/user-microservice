#!/usr/bin/env python

from user_microservice import create_app
import sys

dbfile = len(sys.argv) > 1 and sys.argv[1] or "userdb.db"
port = len(sys.argv) > 2 and sys.argv[2] or 5000

create_app(dbfile=dbfile).run(host="0.0.0.0", port=port)
