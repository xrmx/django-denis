django-denis
==============

Denis helps you recovering accidentally deleted data from a django project.

Rationale
---------

Humans make mistakes, sometimes they delete data accidentally from the ``django admin``
and you have to spend your afternoon recovering data from a db dump. Sometimes the human
is called Denis.

Requirements
------------

- Django ``1.8``

Installation
------------

- ``pip install django-denis``

Usage
-----

Given a queryset ``django-denis`` finds what the django admin would delete and recover
them from a backup database.

Here's an example session:

::

    $ python manage.py shell
    >>> from denis import Denis
    >>> from django.contrib.auth.models import User
    >>> User.objects.filter(pk=40182)
    []
    >>> qs = User.objects.using('backup').filter(pk=40182)
    >>> denis = Denis(qs, using='backup')
    >>> denis.recover(using='default')
    >>> User.objects.using('default').filter(pk=40182)
    <User: cicciopasticcio>

The code above assumes a configuration entry called ``backup`` for ``DATABASES`` in ``settings.py``
that should point to a database containing the data you want to recover.

Be cautious
-----------

Please always test (and test again) recovery on a copy of your database so you can double check
that everything works fine before doing it on your production db.

Of course we don't take any responsibility with this code. Use at your own risk!
