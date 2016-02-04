# Full-Stack-Menu-Project

A simple web app made with Python.

![screenshot](http://downloads.chrisullyott.com/courses/udacity/full-stack/finalproject-demo.jpg)

## Dependencies

**VirtualBox**

https://www.virtualbox.org/

**Vagrant**

https://www.vagrantup.com/

**SQL Alchemy**

http://www.sqlalchemy.org/

**Flask**

http://flask.pocoo.org/

**dicttoxml**

https://pypi.python.org/pypi/dicttoxml

## Setup

Set up VirtualBox and Vagrant to create your own server. With Vagrant installed, run:

```
$ vagrant up
$ vagrant ssh
$ cd <SYNCED PATH TO REPOSITORY>
```

Initialize and fill the database with these scripts.

```
$ python database_setup.py
$ python lotsofmenus.py
```

## Run

Run the web app finalproject.py:

```
$ python finalproject.py
```

The app runs on port `2200`:

```
http://52.89.11.168:2200/
```

## API Endpoints

Available in JSON and XML at the following endpoints:

List all restaurants:

```
http://52.89.11.168:2200/restaurants/json
http://52.89.11.168:2200/restaurants/xml
```

List all menu items for a given RESTAURANT_ID:

```
http://52.89.11.168:2200/restaurants/<RESTAURANT ID>/menu/json
http://52.89.11.168:2200/restaurants/<RESTAURANT ID>/menu/xml
```

List a single menu item:

```
http://52.89.11.168:2200/restaurants/<RESTAURANT ID>/menu/<ITEM ID>/json
http://52.89.11.168:2200/restaurants/<RESTAURANT ID>/menu/<ITEM ID>/xml
```
