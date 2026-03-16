cd C:\LiveProjects\JIvo-Exim\EXIM-backend

echo Pulling frontend code...
git pull

echo Installing python dependencies...
pip install -r requirements.txt

echo running migrations ...
python manage.py migrate

echo collecting static files ...
python manage.py collectstatic --noinput

echo Backend deployed successfully