from fabric.api import task, local, lcd


@task(default=True)
def tasks():
    local('fab -l')


@task
def install():
    local('pip install -e .')
    local('pip install -r test_requirements.txt')


@task
def unit_tests():
    local('flake8')
    local('nosetests tests/')


@task
def integration_tests():
    with lcd('integration_tests'):
        local('python run_test.py')
