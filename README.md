<p align="center">
  <img src="img/logo_light.png#gh-light-mode-only" alt="logo-light" />
  <img src="img/logo_dark.png#gh-dark-mode-only" alt="logo-dark" />
</p>

<p align="center">
  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white" alt="python-badge">
  </a>
  <a href="https://www.djangoproject.com">
    <img src="https://img.shields.io/badge/Django-4.0+-092E20?style=flat&logo=django&logoColor=white" alt="django-badge">
  </a>
    <a href="https://www.django-rest-framework.org/">
    <img src="https://img.shields.io/badge/DRF-3.13.1-a30000?style=flat" alt="drf-badge">
  </a>
  <a href="https://documenter.getpostman.com/view/19098124/UVkvHCLn">
    <img src="https://img.shields.io/badge/Postman-Docs-f06732?style=flat&logo=postman&logoColor=white" alt="postman-badge">
  </a>
  <a href="https://black.readthedocs.io/en/stable/index.html">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="black-badge">
  </a>
  <a href="https://github.com/hmignon/P12_mignon_helene/actions">
    <img src="https://img.shields.io/github/workflow/status/hmignon/P12_mignon_helene/Django%20CI?logo=github" alt="ci-workflow">
  </a>
</p>

# About the project

**OpenClassrooms Python Developer Project #12: Develop a Secure Back-End Architecture Using Django ORM**

_Tested on Windows 10 - Python 3.9.5 - Django 4.1 - DRF 3.13.1_

### Objectives

**API-EpicEvents** is a Customer Relationship Management (*CRM*) API designed for _Epic Events_, 
an events management company.

Epic Events users can:

- Create and update a client database
- Create and manage contracts and organise related events

The RESTful API is implemented with a secured database built with Django ORM and PostgreSQL.

## [:orange_book: Postman documentation](https://documenter.getpostman.com/view/19098124/UVkvHCLn)

Note: Postman docs are currently only available in French ![fr-flag](https://flagcdn.com/16x12/fr.png), 
English ![uk-flag](https://flagcdn.com/16x12/gb.png) version coming soon.

## Post-course optimisation

This project has been optimised after the end of the OpenClassrooms course.
To view the previously delivered version, please check 
[this commit](https://github.com/hmignon/P12_mignon_helene/tree/0ad82d7f9b552faddc864a8154e37bf4377e5d4d).

Improvements made to this project include:

- Adding a Team model
- Providing custom management commands to create dummy data
- Optimising test coverage
- Improving the admin site interface with Jazzmin
- General project refactoring

# Local development

## Clone repository and install dependencies

### Windows

```
git clone https://github.com/hmignon/P12_mignon_helene.git

cd P12_mignon_helene 
python -m venv env 
env\Scripts\activate

pip install -r requirements.txt
```

### MacOS and Linux

```
git clone https://github.com/hmignon/P12_mignon_helene.git

cd P12_mignon_helene 
python3 -m venv env 
source env/bin/activate

pip install -r requirements.txt
```

## Create PostgreSQL database

Install [PostgreSQL](https://www.postgresql.org/download/).
Follow the [documentation](https://www.postgresql.org) to run the server.

Create a new PostgreSQL database with SQL shell (psql) : ```CREATE DATABASE your_db_name;```

## Environment variables : .env file

To generate a .env file, run ```python create_dot_env.py``` and input the info required.

Example of a generated .env file:

    SECRET_KEY=j%yuc7l_wwz5t8d=g)zxh6ol@$7*lwx6n0p)(k$dewlr0hf2u-
    DATABASE_NAME=your_db_name
    DATABASE_USER=your_db_user
    DATABASE_PASS=your_db_password

The Django secret key is randomly generated.

## Migrate the database

To migrate, run ```python manage.py migrate```. The 3 user teams (manager, sales, support) are 
automatically created; to learn more about user teams and their permissions, 
check the [API docs](https://documenter.getpostman.com/view/19098124/UVkvHCLn).

## Create a superuser

Run ```python manage.py create superuser```. Superusers are automatically added to the management team, 
and have access to the admin site.

## Create data

Run the following commands prefixed with ```python manage.py``` to create some dummy data:

| Command                | Description                                                                                                                                                                                                                                                                             |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ```create_data```      | **Create a set of all objects** (15 users, 50 clients, 20 contracts, 10 events). No extra args.                                                                                                                                                                                         |
| ```create_users```     | **Create a set of users.** Args: ```-n``` *or* ```--number``` (default: 15).                                                                                                                                                                                                            |
| ```create_clients```   | **Create a set of clients.** Args: ```-n``` *or* ```--number``` (default: 50).                                                                                                                                                                                                          |
| ```create_contracts``` | **Create a set of contracts.** Args: ```-n``` *or* ```--number``` (default: 20).                                                                                                                                                                                                        |
| ```create_events```    | **Create a set of clients.** Args: ```-n``` *or* ```--number``` (default: 10). <br/>***Note:*** *Events are exclusively related to one signed contract (one to one rel); the command will create as many events as possible if the amount provided is higher than available contracts.* |


# Usage

Run the server with ```python manage.py runserver```. The CRM is browsable via :

- [Postman](https://www.postman.com/);
- [cURL](https://curl.se) commands

Note : CRM access to managers and admins is read-only. Creating, updating and deleting elements is 
available in the admin site.

## Admin site

<p align="center">
    <img src="img/admin_site.gif" alt="Admin site interface" />
    <em>EpicEvents Admin interface</em>
</p>

Tha admin site is available at http://127.0.0.1:8000/admin/. Admin site access is granted to managers 
and superusers.

For a better user experience, the admin interface is customized and *jazzed up* with [Jazzmin](https://django-jazzmin.readthedocs.io).


## Testing, coverage and error logging

Run tests locally with ```python manage.py test```.

Check test coverage with ```coverage run --source='.' manage.py test``` and ```coverage report```.

**Latest coverage report:**

<p align="center">
    <img src="img/coverage_report.png" alt="latest coverage report" />
</p>

All app errors are logged in to ```errors.log```.