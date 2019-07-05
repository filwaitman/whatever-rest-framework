from setuptools import find_packages, setup

from wrf import VERSION

BASE_CVS_URL = 'https://github.com/filwaitman/whatever-rest-framework'


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
    tests_require=[x.strip() for x in open('requirements_test.txt').readlines()],

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
