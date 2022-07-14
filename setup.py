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
    with open("README.md", mode="r", encoding="utf8") as readme_file:
        long_description = readme_file.read()

    with open("requirements.txt", mode="r", encoding="utf8") as requirements_file:
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
        "": [
            "dime_instructions.md",
            "dime_config.yml",
            "dime_explanations/*",
            "dime_cache/*",
            "data/*",
            "models/*",
            "frontend/*",
            "frontend/res/*",
            "frontend/res/images/*",
            "frontend/res/scripts/*",
            "frontend/res/styles/*",
            "frontend/static/*",
            "frontend/static/css/*",
            "frontend/static/js/*",
            "frontend/static/media/*",
            "static/*",
            "templates/*",
            ".env",
            "*.env",
            "*.md",
            "*.js",
            "*.css",
            "*.png",
            "*.py",
        ],
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
        'rasa~=2.8.8',
        'rasa-sdk<3.0.0,>=2.8.1',
        'requests<3.0,>=2.23',
        'ruamel.yaml<0.17.0,>=0.16.5',
        'numpy<1.19,>=1.16',
        'setuptools>=41.0.0',
        'scipy<2.0.0,>=1.4.1',
        'regex<2021.8,>=2020.6',
        'tensorflow<2.4,>=2.3.4',
        'scikit-learn<0.25,>=0.22',
        'pymongo<3.11,>=3.8',
        'tqdm<5.0,>=4.31',
        'pandas<=1.4.3,>=1.3.5',
        'gensim~=4.1.2',
        'flask~=2.1.2',
        'werkzeug~=2.1.2',
        'termgraph~=0.5.3',
        'flask-cors~=3.0.10',
        'waitress~=2.1.2',
        'python-dotenv~=0.20.0',
        'psutil~=5.9.1',
    ],
    entry_points={'console_scripts': ['dime = dime_xai.dime_xai:run_dime_cli']}
)
