# dcrf-chat

### Install dependencies
integration with pycharm https://www.jetbrains.com/help/pycharm/pipenv.html
```
  pipenv install
```

### Create .env file
```
cd src
cp .env.template .env
```

### Run migrations
```
./manage.py migrate
```

### Run sever
```
./manage.py runserver
```

### Run tests
```
./manage.py test
```

### Install pre commit hooks
```
pre-commit install
```

### Manually run all pre commit hooks
```
pre-commit run --all-files
```

### Useful links
- `pipenv` for managing project dependencies: https://pipenv-fork.readthedocs.io/
- `environs` for managing environment variables: https://django-environ.readthedocs.io/en/latest/
- `pre-commit` for managing git pre-commit hooks: https://pre-commit.com
- `isort` for sorting python imports: https://pycqa.github.io/isort/
- `black` for python code formatting: https://black.readthedocs.io
- `mypy` for static type checking: http://mypy-lang.org