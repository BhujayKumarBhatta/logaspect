from setuptools import setup

setup(name='logaspect',
      version='0.0.1',
      description='Datasets for aspect-based sentiment analysis in log files.',
      long_description='Datasets for aspect-based sentiment analysis in log files.',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='aspect-based sentiment',
      url='http://github.com/studiawan/logaspect/',
      author='Hudan Studiawan',
      author_email='studiawan@gmail.com',
      license='MIT',
      packages=['logaspect'],
      install_requires=[
          'nerlogparser'
      ],
      include_package_data=True,
      zip_safe=False)
