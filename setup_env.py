""" Create .env file for EpicEvents project with random secret key and DB info"""

from django.core.management.utils import get_random_secret_key

print('Enter database info')
username = input('Username: ')
password = input('Password: ')

with open(".env", "w") as f:
    f.write(f"SECRET_KEY={get_random_secret_key()}\n")
    f.write(f"DATABASE_USER={username}\n")
    f.write(f"DATABASE_PASS={password}\n")

print("\n.env file created!")
