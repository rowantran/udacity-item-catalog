# Item Catalog

Multi-user item catalog project. Implements Google OAuth and Flask.

## Running
Install [Vagrant](https://www.vagrantup.com/).

Once Vagrant is installed, cd to vagrant/ and run `vagrant up && vagrant ssh`. In the virtual machine, cd to
`/vagrant/catalog` and run `python main.py`. The item catalog can then be accessed at `localhost:5000`.

## Usage
The item catalog provides a human-usable website as well as JSON endpoints for parsing.

To access the website, simply go to `localhost:5000`.

### JSON endpoints
Catalog JSON: `/json`
Category JSON: `/category/<categoryID>/json`
Item JSON: `/category/<categoryID>/<itemID>/json`
