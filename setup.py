from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='npr',
      version='0.1',
      description='NPR API services framework',
      long_description='Self-authenticating module for accessing NPR APIs in Python.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Sound/Audio',
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
