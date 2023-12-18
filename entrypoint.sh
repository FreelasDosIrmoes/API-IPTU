test -d migrations || flask db init

flask db migrate

flask db upgrade

python3 -Bu main.py