Quickstart
==========

Installing the Django Application
---------------------------------

First thing you should create a virtual environment and install all dependencies
since django_tos and ensure that you have installed tos lib.

.. code-block:: bash

    cd django_tos
    sudo pip3 install virtualenv virtualenvwrapper
    source /usr/local/bin/virtualenvwrapper.sh
    sudo apt-get install rabbitmq-server
    mkvirtualenv -a $(pwd) -r requirements/base.txt -p /usr/bin/python3.4 tos_web
    python setup.py develop

Deploy Tree of Science Web
--------------------------

After installing the unit it is only necessary to export the environment
variable settings for the virtual environment and load credentials.
Finally sets up the django server.

.. code-block:: bash

    export DJANGO_SETTINGS_MODULE="treeofscience.settings.development"
    export CREDENTIALS
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

If there is any drawback contact development team ToS