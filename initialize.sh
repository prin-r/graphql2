#! /bin/sh

source venv/bin/activate

pip install -r requirements.txt

python __main__.py --dburi=postgresql://postgres:1234@172.18.0.6:5432 --dbname=graph_test LOOP
