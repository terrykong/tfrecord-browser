from setuptools import setup, find_packages

from tfrecord_browser import __version__

setup(
    name='tfrecord_browser',
    url='https://github.com/terrykong/tfrecord-browser',
    author='Terry Kong',
    author_email='terrycurtiskong@gmail.com',
    scripts=['bin/tfrecord-browser'],
    packages=find_packages(),
    include_package_data=True,
    # Shouldn't include tensorflow here
    install_requires=["urwid", "urwidtrees"],
    #setup_requires=["pytest-runner"],
    #tests_require=["pytest"],
    version=__version__,
    #TODO(terry): add a license?
    description='Read your tfrecord files from the command line',
    long_description=open('README.md').read(),
)
