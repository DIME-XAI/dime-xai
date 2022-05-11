import logging
import sys
from setuptools import (
    setup,
    find_packages,
)

from dime_xai.shared.constants import (
    PACKAGE_VERSION,
    PACKAGE_NAME_PIPY,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if sys.version_info < (3, 7) or sys.version_info >= (3, 9):
    sys.exit('DIME requires Python 3.7 or 3.8')

requirements = None
long_description = None

try:
    with open("README.md", "r") as readme_file:
        long_description = readme_file.read()

    with open("requirements.txt", "r") as requirements_file:
        requirements = requirements_file.readlines()
    requirements = [str.strip(req) for req in requirements]

except Exception as e:
    long_description = "not provided"
    logger.error(f"couldn't retrieve the long "
                 f"package description. {e}")

setup(
    name=PACKAGE_NAME_PIPY,
    version=PACKAGE_VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        # Include special files needed
        # for init project:
        "": ["*.txt", "*.md", "*.bak"],
    },
    description="Explains DIETClassifier model "
                "predictions in Rasa chatbot framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thisisishara/dime-xai",
    author="Ishara Dissanayake",
    author_email="thisismaduishara@gmail.com",
    license='Apache License 2.0',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: GPU",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    install_requires=requirements or [
        'regex~=2021.7.6',
        'rasa~=2.8.8',
        'rasa-sdk~=2.8.4',
        'numpy~=1.18.5',
        'scipy~=1.7.3',
        'tensorflow~=2.3.4',
        'gensim~=4.1.2',
        'scikit-learn~=0.24.2',
        'flask~=2.0.3',
        'werkzeug~=2.0.3',
        'requests~=2.27.1',
        'tqdm~=4.62.3',
        'pandas~=1.3.5',
        'termgraph~=0.5.3',
        'setuptools~=58.0.4',
        'flask-cors~=3.0.10',
    ],
    entry_points={'console_scripts': ['dime = dime_xai.dime_xai:run_dime_cli']}
)
