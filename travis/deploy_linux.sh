wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda info -a
conda create -n test-environment python=$TRAVIS_PYTHON_VERSION
source activate test-environment

python setup.py bdist_wheel sdist
pip install twine
twine upload dist/* --skip-existing
