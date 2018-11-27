.ONESHELL:
clean:
	rm -rf build;
	rm -rf dist;
	rm -rf procbridge.egg-info

build:
	# https://packaging.python.org/tutorials/packaging-projects/
	python3 setup.py sdist bdist_wheel

upload_test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload:
	twine upload dist/*
