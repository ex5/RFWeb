RFWeb
=====

Web-app for browsing and scheduling Robot Framework tests, inspired by RFDoc

Requirements
=====

 * [Python-2.7](http://www.python.org/getit/releases/2.7.3/)
 * [MySQL-python >= 1.2.3](http://sourceforge.net/projects/mysql-python/)
 * [lxml-2.3](http://lxml.de/installation.html)
 * Django-1.3
 * [RobotFramework 2.7](http://code.google.com/p/robotframework/downloads/list)
 * [django-dajaxice-0.2](https://github.com/jorgebastida/django-dajaxice/)
 * [django-dajax-0.8.4](https://github.com/jorgebastida/django-dajax)
 * mod_wsgi-3.3 (if you want to deploy it for some strange reason)

Installation
=====

Python 2.7
==

If you need to install Python 2.7 separately from any other Python that is already installed in the system (e.g., if it's CentOS you are dealing with), then you might want to build Python from source:

    #!/bin/sh

    PYTHON_PREFIX=/opt/python2.7

    wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz
    tar -zxvf Python-2.7.3.tgz
    cd Python-2.7.3.tgz
    make clean
    ./configure --prefix=$PYTHON_PREFIX --exec-prefix=$PYTHON_PREFIX --libexecdir=$PYTHON_PREFIX/lib --with-pth --with-fpectl --with-system-expat --with-threads --enable-shared --enable-unicode --enable-big-digits --with-signal-module --with-pydebug
    make
    make install
    touch /etc/ld.so.conf.d/python2.7.conf
    echo $PYTHON_PREFIX/lib > /etc/ld.so.conf.d/python2.7.conf
    ldconfig 

Setuptools are needed too:

    wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg#md5=fe1f997bc722265116870bc7919059ea
    ln -s $PYTHON_PREFIX/bin/python2.7 /usr/bin/python2.7
    /bin/sh setuptools-0.6c11-py2.7.egg --prefix=$PYTHON_PREFIX
    ln -s $PYTHON_PREFIX/bin/easy_install-2.7 /usr/bin/easy_install-2.7


After that MySQL-python and lxml can be easily installed:

    easy_install-2.7 MySQL-python
    easy_install-2.7 lxml


Setting up RobotFramework 2.7
==

    wget http://robotframework.googlecode.com/files/robotframework-2.7.5.tar.gz
    tar -zxvf robotframework-2.7.5.tar.gz
    cd robotframework-2.7.5
    python2.7 setup.py install


Setting up Django
==

Setting up Dajaxice
==

    wget https://github.com/downloads/jorgebastida/django-dajaxice/django-dajaxice-0.2.tar.gz
    tar -zxvf django-dajaxice-0.2.tar.gz
    cd django-dajaxice-0.2
    python2.7 setup.py install


Setting up Dajax
==

    wget https://github.com/downloads/jorgebastida/django-dajax/django-dajax-0.8.4.tar.gz
    tar -zxvf django-dajax-0.8.4.tar.gz
    cd django-dajax-0.8.4
    python2.7 setup.py install


Preparing database
==
