#!/usr/bin/python
sys.path.insert(0, "/var/www/catalog/")

from catalog import finalproject as application
application.secret_key = 'super_secret_key'
