from setuptools import setup, find_packages


def readme():
    with open("README.md", 'r') as f:
        return f.read()


setup(
    name="insight_matrix",
    description="Clustering tools for designers.",
    version="0.1.0",
    long_description=readme(),
    author="John Jung",
    author_email="john@johnjung.us",
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/johnjung/insight_matrix',
    entry_points={
      'console_scripts': [
        'insight_matrix = insight_matrix.__main__:main'
      ]
    }
)
