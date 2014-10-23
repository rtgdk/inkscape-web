
source pythonenv/bin/activate

MANAGE="./inkscape/manage.py"

mkdir -p locale

$MANAGE makemessages --locale=$1 --ignore=PIL --ignore=html5lib --ignore=compositekey --ignore=easy_thumbnails --ignore=south

