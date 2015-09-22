from setuptools import setup, find_packages
import os

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Environment :: Console',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    author="Riccardo Magliocchetti",
    author_email="riccardo.magliocchetti@gmail.com",
    name='django-denis',
    version='0.1.0',
    description='Denis helps you recovering accidentally deleted data from a django project',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url="https://github.com/xrmx/django-denis",
    license='MIT License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'django>=1.8',
    ],
    test_suite='runtests.runtests',
    packages=find_packages(exclude=["test_denis_project"]),
    include_package_data=True,
    zip_safe = False,
)

