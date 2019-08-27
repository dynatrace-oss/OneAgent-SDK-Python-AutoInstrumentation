from setuptools import setup, find_packages

setup(name='autodynatrace',
      version='1.0.4',
      packages=find_packages(),
      install_requires=['wrapt>=1.11.2', 'oneagent-sdk>=1.2.1'],
      author='David Lopes',
      author_email='davidribeirolopes@gmail.com',
      description='Auto instrumentation for the OneAgent SDK',
      long_description='THe autodynatrace package will auto instrument your python apps',
      url='https://github.com/dlopes7/autodynatrace',
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent"]
      )
