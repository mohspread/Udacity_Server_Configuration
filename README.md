# Udacity Items Catalog

The items catalog is the 2nd Project in Udacity's Fullstack Nanodegree.


### Features

  - You can signup/signin and create your own favourite movies catalog by creating categories and sub-items inside those categories. 
  - Only you has the access to modify your list or categories, so don't worry!
  - You must login or signup to be able to create categories or items, Otherwise you can only view the existing items.
  

### Tools Needed:

Items Catalog uses a number of tools to work properly:

* [Python](https://www.python.org/downloads/windows/)
* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/)
* [Git](https://git-scm.com/downloads)

### Installation

Install all the above tools.
Clone this repo by going to your desired location
* Right click anywhere and choose ```Git bash here ```, Then use the following console commands
```sh
$ git clone https://github.com/mohspread/Udacity-Items-Catalog/ catalog
```
Launch Vagrant with the following commands:
```sh
$ vagrant up
```
Then,
```sh
$ vagrant ssh
```
Change directory to Vagrant folder
```sh
$ cd /vagrant
```
Setup the database
```sh
$ Python database_setup.py
```
Populate the database with some data
```sh
$ Python lotsofmenus.py
```
Launch main project file:
```sh
$ Python project.py
```
Open the browser and go to http://localhost:5000

### JSON  Endpoints

Returns JSON format of all items and categories together
```sh
/catalog/JSON
```

Returns JSON format of all categories
```sh
/categories/JSON
```

Returns JSON format of all items
```sh
/items/JSON
```

Returns JSON format of the all items inside specific category
```sh
/categories/<int:category_id>/menu/JSON
```

Return JSON format of the a single item inside a category
```sh
/categories/<int:category_id>/menu/<int:item_id>/JSON
```

### Credits
Created by Mohamed Ahmed for Udacity
