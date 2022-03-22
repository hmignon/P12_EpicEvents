# Projet 12 DA-Python OC (Hélène Mignon)

***Livrable du Projet 12 du parcours D-A Python d'OpenClassrooms***

**API-EpicEvents** est une API RESTful conçue pour une entreprise de conseil et de gestion évènementielle.

L'application permet aux utilisateurs de créer et mettre à jour une base de données clients, 
de créer et d'assurer le suivi des contrats et des évènements.

Une base de donnée sécurisée est mise en œuvre avec Django ORM et PostgreSQL.

_Testé sous Windows 10 - Python 3.9.5 - Django 4.0.2 - DRF 3.13.1_

## Documentation

Pour plus de détails sur le fonctionnement de cette API, se référer à sa 
[documentation](https://documenter.getpostman.com/view/19098124/UVkvHCLn) (Postman), 
et le [diagramme entité-relation](img/erd_epicevents.png) du CRM.

## Initialisation du projet

### Récupération du projet et installation des dépendances

#### Windows
```
git clone https://github.com/hmignon/P12_mignon_helene.git

cd P12_mignon_helene 
python -m venv env 
env\Scripts\activate

pip install -r requirements.txt
```

#### MacOS et Linux
```
git clone https://github.com/hmignon/P12_mignon_helene.git

cd P12_mignon_helene 
python3 -m venv env 
source env/bin/activate

pip install -r requirements.txt
```

### Créer la base de données

Installer [PostgreSQL](https://www.postgresql.org/download/)
Se référer à la [documentation](https://www.postgresql.org) pour le lancement du serveur.

Créer la base de données avec SQL shell (psql) : ```CREATE DATABASE epic_events;```


### Variables d'environnement

Pour générer un fichier .env, lancer le script ```python setup_env.py```.
Entrer le nom d'utilisateur et le mot de passe de la base de données précédemment créée.

Une clé secrète Django sera automatiquement générée.


### Migration de la base de données

```
python manage.py migrate
```

### Créer un superuser

```
python manage.py create superuser
```

### Lancer le serveur Django

```
python manage.py runserver
```

## Utilisation

Il est possible de naviguer dans l'API avec différents outils :

- la plateforme [Postman](https://www.postman.com/) ;
- l'outil de commandes [cURL](https://curl.se)

### Administration

Le site d'administration Django est accessible via http://127.0.0.1:8000/admin/

Cet accès est possible pour tous les utilisateurs de l'équipe de gestion (management) et les superusers.

### Logging

L'application consigne les erreurs et exceptions dans le fichier [errors.log](errors.log).

### Tests

Il est possible d'effectuer les tests via la commande :

```
python manage.py test
```
Rapport de test le plus récent :

![Rapport de test](img/test_report.png)

Les tests couvrent 98% de l'application (voir [rapport](img/coverage_report.png) le plus récent). 
Pour effectuer le test de couverture :

```
coverage run --source='.' manage.py test
coverage report
```