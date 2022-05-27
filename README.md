# DIME XAI 0.0.4a6 Pre-release 👽
### Pre-release of DIME (Dual Interpretable Model-agnostic Explanations) mainly aimed at Explaining DIET Classifiers in RASA 2.X.X. Models.

## Features 🦄

- Explain RASA DIET Classifiers using feature importance
- Generate dual feature importance scores
- No Surrogate models, thus efficient
- Total confidence drop as the feature importance score
- Explain both local and REST models
- Easy to use DIME CLI

## What's Cooking? 🍪

- Intent-based Importance 
- DIME Server, a complete GUI
- DIME for Notebooks
- Stopwords List Generation

## Limitations and Known Issues 🤏🏽

- Disabled Global Importance for REST models due to performance issues
- Explaining RASA models locally on Notebooks such as CoLab is not supported yet due to dependency issues (NumPy)
- Benchmark tests are in progress

📦 PyPi: https://pypi.org/project/dime-xai/0.0.4a6/  
🪵 Full Changelog: https://github.com/thisisishara/dime-xai/commits/0.0.4a6