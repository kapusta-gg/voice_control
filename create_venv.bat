python -m venv .venv
call .venv/Scripts/activate
pip install -r voice/requirements.txt
pip install -r robot/requirements.txt
python -m spacy download ru_core_news_md