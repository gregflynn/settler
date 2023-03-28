from distutils.core import setup


setup(
    name='settler',
    version='0.5.1',
    author='Greg Flynn',
    author_email='gregflynn42@gmail.com',
    url='https://github.com/gregflynn/settler',
    packages=['settler'],
    provides=['settler'],
    install_requires=[
        'sqlalchemy>=1.4'
    ]
)
