#!/usr/bin/python
sys.path.insert(0, "/var/www/catalog/")

import catalog as application
application.secret_key = 'super_secret_key'
