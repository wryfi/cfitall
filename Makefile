wheel:
	rm -rf dist/*
	pipenv lock -r > requirements.txt
	pipenv run python setup.py sdist bdist_wheel
	rm requirements.txt

pypi_test: wheel
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi: wheel
	pipenv run twine upload dist/*
