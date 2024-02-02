build:
    rm -f dist/*
    pipenv requirements > requirements.txt
    pipenv run python -m build
    rm requirements.txt

pypi_test: build
    pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi: build
    pipenv run twine upload dist/*
