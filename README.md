# App Details

#### IP address

`52.89.11.168`

#### App URL

[http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com/](http://ec2-52-89-11-168.us-west-2.compute.amazonaws.com/)

#### Login

_Place the provided Udacity private key file in your local_ `~/.ssh` _directory, and run:_

```
ssh -i ~/.ssh/udacity_key.rsa grader@52.89.11.168 -p 2200
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

```
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

#### If some downloads failed, try again

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

#### Add a sudoers file for "grader"

```
$ sudo nano /etc/sudoers.d/grader
```
_Add to this line to the sudoers file:_

```
grader ALL=(ALL:ALL) ALL
```

#### Access and copy the existing public key for user "root"

```
$ sudo cat /home/root/.ssh/authorized_keys
```

#### Paste this public key into the authorized_keys file for user "grader"

```
$ sudo nano /home/grader/.ssh/authorized_keys
```

_The public key is also available in this repository, as_ `ssh-rsa.pub`_._

#### Verify that you can now switch between these users successfully

```
$ su grader
$ su root
$ su grader
```

_Reset the password for the user "grader" and use a complex, secure password:_

```
$ passwd grader
```

_We've now given_ `grader` _sudo access. Stay logged in as_ `grader` throughout the rest of the setup.

## 4. Disable root login

#### Remove SSH key from root user

_Delete all the contents in the authorized keys file for root._

``` 
$ sudo nano /home/root/.ssh/authorized_keys
```
_The root user can no longer log in using the provided SSH keys. Let's now disable SSH access for root altogether in the following steps._

#### Change default SSH port and disable root login

_Remember, be sure to be logged in as_ `grader` _at this point._

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
$ ssh -i ~/.ssh/udacity_key.rsa grader@52.89.11.168 -p 2200
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
_Install these items:_
#### PIP, environments

```
$ sudo apt-get install python-pip
$ sudo pip install virtualenv
```

#### The virtual environment

_Create a virtual environment with **virtualenv**. Your environment's name can be "venv" or anything._

```
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
$ sudo apt-get install postgresql
```

#### Other needs
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

_Add the following rules. "52.89.11.168" is the IP address of the app above._
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

## 12. Required app changes

#### Add client secret files
_The secrets files don't exist in this repository for security reasons._
```
$ cd /var/www/catalog/catalog
$ sudo mkdir oauth
$ sudo nano google_client_secrets.json
$ sudo nano fb_client_secrets.json
```

_Ok, now test the app!_
```
$ sudo python __init__.py 
```

# ### DONEZO ########################  #########################

# Helpful commands

View Apache's error logs

```
$ sudo cat /var/log/apache2/error.log
```

Delete an entire directory ([cyberciti.biz](http://www.cyberciti.biz/faq/linux-delete-folder-recursively/))

```
$ sudo rm -rf <folderName>
```

# Other Helpful Resources

[Digital Ocean - How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

[Digital Ocean - Initial Server Setup with Ubuntu 12.04](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-12-04)

[Ubuntu - Uncomplicated Firewall](https://help.ubuntu.com/community/UFW)

[Udacity Getting Started Guide](https://docs.google.com/document/d/1J0gpbuSlcFa2IQScrTIqI6o3dice-9T7v8EDNjJDfUI/pub)

[stueken's project example](https://github.com/stueken/FSND-P5_Linux-Server-Configuration)

[Udacity Forums](https://discussions.udacity.com/t/linux-server-configuration-final-sql-alchemy-v-psql/44448)

[Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

[Error message when I run sudo: unable to resolve host (none)](http://askubuntu.com/questions/59458/error-message-when-i-run-sudo-unable-to-resolve-host-none)

