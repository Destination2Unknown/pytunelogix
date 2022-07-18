from setuptools import setup, find_packages

setup(
    name='pytunelogix',
    version='1.1.14',
    license='MIT',
    author="Destination2Unknown",
    author_email='destination0b10unknown@gmail.com',
    description='PID tuner, logger and simulator',
    long_description='PID tuner, logger and simulator, with multiple tuning methods',
    packages=find_packages(),
    url='https://github.com/Destination2Unknown/pytunelogix',
    keywords='PID Tuner',
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=[
          'scipy',
          'numpy',
          'matplotlib',
          'pylogix',
          'pandas',
      ],
)