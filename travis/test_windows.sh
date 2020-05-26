conda create -n test-environment python=$TRAVIS_PYTHON_VERSION
source activate test-environment

pip install -e .[dev]
black .\ -l 79 --target-version py37 --check
