from setuptools import setup, find_packages


def readme():
    with open("README.md", 'r') as f:
        return f.read()


setup(
    name="planning_tools",
    description="Tools for design methods and design planning.",
    version="0.1.0",
    long_description=readme(),
    author="John Jung",
    author_email="john@johnjung.us",
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/johnjung/planning_tools",
    entry_points={
      'console_scripts': [
        'cardsort = planning_tools.cardsort.main',
        'matrix = planning_tools.matrix.main',
        'similarity = planning_tools.similarity.main'
      ]
    }
)
