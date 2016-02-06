# App Details

#### IP address

`52.89.11.168`

#### App URL

[http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com/](http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com/)

#### Login

_Place the provided Udacity private key file in your local_ `~/.ssh` _directory, and run:_

```
$ ssh -i ~/.ssh/grader.rsa grader@52.89.11.168 -p 2200
```

_As a security precaution,_ `root` _login has been disabled. However, the user_ `grader` _has been given sudo access._


# Server Setup Steps!

_Here are the steps I personally took to complete this project. There are a lot of steps!_

## 1. Initialize Amazon AWS server

#### Create an Amazon AWS virtual machine and get the private SSH key, VM IP address

```
https://www.udacity.com/account#!/development_environment
```

#### Log in as the default root user

_First, download the supplied private key to your computer, chown it, and use it to log in:_

```
$ chmod 600 ~/.ssh/udacity_key.rsa
$ ssh -i ~/.ssh/udacity_key.rsa root@52.89.11.168
```

## 2. Update the server

#### View updatable packages

```
$ sudo apt-get update
```

#### Upgrade packages to latest available

```
$ sudo apt-get upgrade
```

#### If some downloads failed, try again with:

```
$ sudo apt-get upgrade --fix-missing
```

## 3. Create new sudo-enabled user

#### Install "finger" app

_Not required, but helpful for user management_

```
$ sudo sudo apt-get install finger
```

#### Create the new user, "grader"

```
$ sudo adduser grader
```

#### Create a sudoers file for "grader"

```
$ sudo nano /etc/sudoers.d/grader
```

_Add to this line to this sudoers file:_

```
grader ALL=(ALL:ALL) ALL
```

_Back on the local machine, generate a new SSH keypair with a passphrase. I called mine "grader"._

```
$ ssh-keygen
```

_Rename the PRIVATE KEY file "grader" to "grader.rsa"_

_Open and copy the contents of the public key (the "grader.pub" file)_

_SSH into the server as root again, and add the new public key to user "grader"_
```
$ sudo mkdir /home/grader/.ssh
$ sudo nano /home/grader/.ssh/authorized_keys
```

_Paste the public key in this file and save._

_The public key is also available in this repository, as_ `grader.pub`_._

#### Verify that you can now switch between these users successfully

```
$ su grader
$ su root
$ su grader
```

_Reset the password for the user "grader":_

```
$ passwd grader
```

_Log out, and verify that you can log in as "grader". On your local operating system, you will be asked to enter your passphrase._

```
$ ssh -i ~/.ssh/grader.rsa grader@52.89.11.168
```

_If you can successfully log in, we've now given_ `grader` _sudo access. Stay logged in as_ `grader` _throughout the rest of the setup._


## 4. Disable root login

**WARNING** _Here we will be disabling root access, so make sure you can successfully log in with sudo access with "grader"! If you cannot log in and/or cannot use "sudo" commands, you must not proceed!_

#### Remove SSH key from root user

_Delete all the contents in the authorized keys file for root._

```
$ sudo nano /home/root/.ssh/authorized_keys
```
_The root user can no longer log in using the provided SSH keys. Let's now disable access for root altogether in the following steps and add more security updates._

#### Change default SSH port and disable root login

_Remember, be sure to have logged in as_ `grader` _at this point._

```
$ sudo nano /etc/ssh/sshd_config
```

Change `Port 22` to `Port 2200`

Change `PermitRootLogin ...` to `PermitRootLogin no`

Change `PasswordAuthentication ...` to `PasswordAuthentication no`

_Restart sshd:_

```
$ sudo service ssh restart
```

_This will restart the SSH service and apply our previous login changes. From now on, you will need to log in with:_

```
$ ssh -i ~/.ssh/grader.rsa grader@52.89.11.168 -p 2200
```

## 5. Edit ports and firewall

_Use the Uncomplicated Firewall tool to configure a simple firewall for the virtual machine._

#### Configure allowed connections:

```
$ sudo ufw default deny incoming
$ sudo ufw default allow outgoing
```

```
$ sudo ufw allow ssh
$ sudo ufw allow 2200
$ sudo ufw allow 2200/tcp
$ sudo ufw allow 80
$ sudo ufw allow 80/tcp
$ sudo ufw allow 123
$ sudo ufw allow 123/tcp
```

#### Enable firewall

**WARNING! If the previous steps were not successful, enabling the firewall may prevent ALL user access to this server!**

_To verify the aforementioned steps were successful, you can view all entered UFW rules using the following command (tip from [askubuntu.com](http://askubuntu.com/questions/30781/see-configured-rules-even-when-inactive)):_

```
$ sudo grep '^### tuple' /lib/ufw/user*.rules
```

_When you are ready, activate the firewall and check its status:_

```
$ sudo ufw enable
$ sudo ufw status
```

## 6. Set timezone to UTC

_Check the current timezone with the_ `date` _command:_
```
$ date
Mon Feb  1 12:35:12 UTC 2016
```

_If timezone is not **UTC**, change it here in the timezone file:_

```
$ sudo nano /etc/timezone
```

## 7. Install Apache HTTP Server and WSGI

_Many of the following steps follow Digital Ocean's tutorial, [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)._ It is not recommended to skip any of these steps!

#### Install Apache 2:

```
$ sudo apt-get install apache2
```

#### Install WSGI for Apache:

_WSGI is an Apache helper for Python applications. (For more info, see [mod_wsgi](http://www.modwsgi.org/))_

```
$ sudo apt-get install python-setuptools
$ sudo apt-get install libapache2-mod-wsgi
```

#### Enable mod_wsgi, if it isn't already
```
$ sudo a2enmod wsgi
```

#### Restart Apache
```
$ sudo service apache2 restart
```

_At this point, visiting the app URL in the browser should bring us to an Apache landing page, saying, "It works!"_

## 8. Install Git and load app

#### Install Git

```
$ sudo apt-get install git-all
```
_If you like, you may configure the Git installation with..._
```
$ git config --global user.name "<YOUR NAME>"
$ git config --global user.email "<YOUR EMAIL ADDRESS>"
```

#### Download the repository

_Create a folder inside the_ `www` _folder called "catalog" and_ `cd` _into this folder._

```
$ cd /var/www
$ sudo mkdir catalog
$ cd catalog
```

_Clone this project's code into a new folder called "catalog". Yes, being a little redundant here, but we're following the [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps) method._

```
$ cd /var/www/catalog
$ sudo git clone https://github.com/chrisullyott/udacity-fsnd-final.git catalog
```

_Your cloned repository will now live inside "/var/www/catalog/catalog". This repo contains all of the basic components of a Flask app._

## 9. Install app and its dependencies

_Before installing, go ahead and_ `cd` _into "/var/www/catalog/catalog", where our app lives. Just to prepare you, when we're done with this, our app's file structure will look like this:_

```
|var
|----www
|--------catalog
|----------------catalog
|-----------------------__init__.py
|-----------------------static
|-----------------------templates
|-----------------------venv
|----------------catalog.wsgi
```

#### Install PIP
```
$ sudo apt-get install python-pip
```

#### Create virtual environment

_Create a virtual environment with **virtualenv**. Your environment's name can be "venv" or anything._
```
$ sudo pip install virtualenv
$ sudo virtualenv venv
```

_Now activate this environment_
```
$ sudo source venv/bin/activate
```

_With the virtual environment activated, it's time to install the app's dependencies inside it._

#### Flask and DB software
```
$ sudo pip install Flask
$ sudo pip install sqlalchemy
$ sudo pip install Flask-SQLAlchemy
$ sudo pip install psycopg2
$ sudo apt-get install python-psycopg2
```

#### More app software
```
$ sudo pip install oauth2client
$ sudo pip install httplib2
$ sudo pip install requests
```

## 10. Configure a Virtual Host in Apache

_Create apache virtual host..._
```
$ sudo nano /etc/apache2/sites-available/catalog.conf
```

_Add the following rules to the configuration file. "52.89.11.168" is the IP address of the app above._
```
<VirtualHost *:80>
    ServerName 52.89.11.168
    ServerAdmin admin@mywebsite.com
    WSGIScriptAlias / /var/www/catalog/catalog.wsgi
    <Directory /var/www/catalog/catalog/>
            Order allow,deny
            Allow from all
    </Directory>
    Alias /static /var/www/catalog/catalog/static
    <Directory /var/www/catalog/catalog/static/>
            Order allow,deny
            Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
_Now, enable this virtual host:_
```
$ sudo a2ensite catalog
```

## 11. Configure the WSGI file
```
$ cd /var/www/catalog
$ sudo nano catalog.wsgi
```

_Add the following to this file:_
```
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalog/")

from catalog import app as application
application.secret_key = 'super_secret_key'
```

_This is a good time to restart apache:_
```
$ sudo service apache2 restart
```

_The warning "Could not reliably determine the VPS's fully qualified domain name..." can be safely ignored, or even turned off [askubuntu.com](http://askubuntu.com/questions/256013/could-not-reliably-determine-the-servers-fully-qualified-domain-name)_

## 12. Configure PostgreSQL

_Since we will be running the database on this server, we will need to make some changes!_

_From [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps)_

#### Check that PostreSQL is installed

_This should return the location of the Postgres binary. If not, go back and install PostreSQL._
```
$ which psql
```

#### Install PostgreSQL
```
$ sudo apt-get install postgresql postgresql-contrib
```

#### Secure PostgreSQL

_Because of the handy "peer" authentication feature, PostgreSQL automatically grants access to the "postres" user. This is helpful at first, but let's not use this for our app, for security reasons._

_Open PostgreSQL config file:_
```
$ sudo nano /etc/postgresql/9.3/main/pg_hba.conf
```

_In this file, also remove any specified connections that aren't local. (After installation, there weren't any to begin with, but it's good practice to check)._

_Restart PostgreSQL_
```
$ sudo service postgresql restart
```

_Now change password for user "postgres"_
```
$ sudo passwd postgres
```

_Create PostgreSQL role for handling the DB, and choose a password (I just used "catalog" again to keep things simple):_
```
$ sudo su - postgres
$ psql
postgres=# CREATE ROLE catalog;
postgres=# ALTER USER catalog WITH PASSWORD 'catalog';
```

_Create the app database with this user._
``` 
postgres=# CREATE DATABASE catalog WITH OWNER catalog;
```

_Revoke all access rights except to 'catalog' user:_
```
postgres=# \c catalog;
postgres=# REVOKE ALL ON SCHEMA public FROM public;
postgres=# GRANT ALL ON SCHEMA public TO catalog;
```

_Log out of PostgreSQL, and restart it_
```
postgres=# \q
$ sudo service postgresql restart
```

_If not already changed, change the app's sqlite database setup to PostgreSQL:_
```
$ sudo nano /var/www/catalog/catalog/database_setup.py

# engine = create_engine('sqlite:///restaurantmenuwithusers.db')
engine = create_engine("postgresql://catalog:catalog@localhost/catalog")
```

```
$ sudo nano /var/www/catalog/catalog/__init__.py

# engine = create_engine('sqlite:///restaurantmenuwithusers.db')
engine = create_engine("postgresql://catalog:catalog@localhost/catalog")
```

```
$ sudo nano /var/www/catalog/catalog/lotsofmenus.py

# engine = create_engine('sqlite:///restaurantmenuwithusers.db')
engine = create_engine("postgresql://catalog:catalog@localhost/catalog")
```

_If not already changed, use the full path to the_ `oauth` _directory wherever it's used. There is a cleaner way to do this, but using the_ `os`__
```
$ sudo nano /var/www/catalog/catalog/__init__.py

$ # oauth/google_client_secrets.json
$ /var/www/catalog/catalog/oauth/google_client_secrets.json
```

_Now, run the database setup!_
```
$ sudo python database_setup.py
$ sudo python lotsofmenus.py
```

## 13. Reconfigure Google OAuth for connected services

#### Add client secret files to app

_The secrets files don't exist in this repository for security reasons, so we'll need to add them manually._
```
$ cd /var/www/catalog/catalog
$ sudo mkdir oauth
$ sudo nano google_client_secrets.json
$ sudo nano fb_client_secrets.json
```

#### Configure Google OAuth

[Google App Credentials](https://console.developers.google.com/apis/credentials?project=udacity-restaurant-menu-1159)

_Add to Authorized JavaScript origins:_
```
http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com
```

_Add to Authorized redirect URIs:_
```
http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com/restaurants
```

#### Configure Facebook OAuth

[Facebook App Dashboard](https://developers.facebook.com/apps/968671983206543/dashboard/)

[Facebook App OAuth Setup](https://developers.facebook.com/apps/968671983206543/settings/advanced/)

_Change authorized app domain and allowed OAuth URIs:_
```
ec2-52-89-11-168.us-west-2.compute.amazonaws.com
```

## 14. Additional security

_Let's be sure to prevent public access to a few directories via htaccess. This can be done with file permissions or in the Apache configuration file for this site also, but starting an .htaccess file could be useful in the future. Also, this helps keep rules for app-specific directories in one place._
```
$ sudo nano /var/www/catalog/catalog/.htaccess

RedirectMatch 404 /\.git  
RedirectMatch 404 /\oauth  
```

## 15. Run!

_Ok, now let's run the app! I would say "test" the app, but that doesn't sound as hopeful!_
```
$ sudo python __init__.py
```

_Load the app at:_

[http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com/](http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com/)


_Check the error logs for any mention of problems:_
```
$ sudo cat /var/log/apache2/error.log
```

# Helpful commands used

**View Apache's error logs**
```
$ sudo cat /var/log/apache2/error.log
```

**Delete user**
```
$ sudo userdel <username>
```

**Delete an entire directory** ([cyberciti.biz](http://www.cyberciti.biz/faq/linux-delete-folder-recursively/))
```
$ sudo rm -rf <folderName>
```

# Other resources used

[Digital Ocean - How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

[Digital Ocean - Initial Server Setup with Ubuntu 12.04](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-12-04)

[Ubuntu - Uncomplicated Firewall](https://help.ubuntu.com/community/UFW)

[Udacity Getting Started Guide](https://docs.google.com/document/d/1J0gpbuSlcFa2IQScrTIqI6o3dice-9T7v8EDNjJDfUI/pub)

[stueken's project example](https://github.com/stueken/FSND-P5_Linux-Server-Configuration)

[Udacity Forums](https://discussions.udacity.com/t/linux-server-configuration-final-sql-alchemy-v-psql/44448)

[Error message when I run sudo: unable to resolve host (none)](http://askubuntu.com/questions/59458/error-message-when-i-run-sudo-unable-to-resolve-host-none)


