from distutils.core import setup, find_packages


config = {
    'name': 'settler',
    'version': '0.1.2',
    'author': 'Greg Flynn',
    'author_email': 'gregflynn42@gmail.com',
    'url': 'https://github.com/gregflynn/settler',
    'packages': find_packages(exclude=['tests', 'integration_tests'])
}


setup(**config)
