from setuptools import setup
from future import standard_library
standard_library.install_aliases()

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='npr',
      version='0.1',
      description='NPR cloud framework',
      long_description='Self-authenticating module for accessing NPR APIs in Python.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
      ],
      keywords='public radio stream metadata api service',
      url='http://github.com/perrydc/npr',
      author='Demian Perry',
      author_email='dperry@npr.org',
      license='MIT',
      packages=['npr'],
      install_requires=[
          'requests','json','re','os','ast','sys',
      ],
      include_package_data=True,
      zip_safe=False)
