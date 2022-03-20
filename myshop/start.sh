echo " " > /etc/apt/sources.list&&
echo "deb http://mirrors.aliyun.com/debian jessie main" >> /etc/apt/sources.list&&
echo "deb http://mirrors.aliyun.com/debian jessie-updates main" >> /etc/apt/sources.list&&
apt-get update&&
apt-get install -y libtinfo5 --allow-remove-essential&&
apt-get install -y vim&&
apt-get install -y cron&&
service cron start&&
cp -f /var/www/html/myshop/scripts/admin.py /usr/local/lib/python3.8/site-packages/haystack/admin.py&&
cp -f /var/www/html/myshop/scripts/forms.py /usr/local/lib/python3.8/site-packages/haystack/forms.py&&
python manage.py collectstatic --noinput&&
python manage.py makemigrations&&
python manage.py migrate&&
python manage.py crontab add&&
python manage.py crontab show&&
uwsgi --ini /var/www/html/myshop/uwsgi.ini