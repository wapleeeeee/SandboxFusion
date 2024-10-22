set -o errexit

rm -f ~/.condarc
conda create -n sandbox-runtime -y python=3.10

source activate sandbox-runtime

pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip install -r ./requirements.txt --ignore-requires-python

# for NaturalCodeBench python problem 29
python -c "import nltk; nltk.download('punkt')"

# for CIBench nltk problems
python -c "import nltk; nltk.download('stopwords')"

pip cache purge
conda clean --all -y
