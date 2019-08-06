import sys

from setuptools import find_packages, setup

from wrf import VERSION

BASE_CVS_URL = 'https://github.com/filwaitman/whatever-rest-framework'


def get_tests_require():
    django_1x_version = 'Django==1.11.23'
    django_2x_version = 'Django==2.2.3'
    lines = [x.strip().split(' ;')[0] for x in open('requirements_test.txt').readlines() if x]

    if sys.version_info.major < 3:
        lines.remove(django_2x_version)
    else:
        lines.remove(django_1x_version)

    return lines


setup(
    name='whatever-rest-framework',
    packages=find_packages(),
    include_package_data=True,
    exclude=['tests'],
    version=VERSION,

    author='Filipe Waitman',
    author_email='filwaitman@gmail.com',

    description='RESTful API framework for your project, whatever tools you are using.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",

    url=BASE_CVS_URL,
    download_url='{}/tarball/{}'.format(BASE_CVS_URL, VERSION),

    install_requires=[x.strip() for x in open('requirements.txt').readlines()],

    test_suite='tests',
    tests_require=get_tests_require(),

    keywords=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Flask',
        'Framework :: Pyramid',
    ],
)
