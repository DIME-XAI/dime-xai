### DIME (Dual Interpretable Model-agnostic Explanations) is mainly aimed at Explaining DIET Classifiers in RASA 2.8.X. Models.

## Features 🦄
- Explains RASA DIET Classifiers using feature importance
- Generates dual feature importance scores (Global FI + Local FI)
- Efficient
- Total confidence drop as the feature importance score
- Able to explain both local and REST Rasa models
- Easy to use DIME CLI
- GUI with a dedicated server on-demand
- Generate, Store, Download, Upload, Peak DIME explanations. Read more on [docs](https://dime-xai.github.io)
- Supports Sinhalese unicode / fully Sinhala-English code-switchable

## What's Cooking? 🍪
- DIME for Jupyter Notebooks
- Stopwords List Generation
- DIME Example Notebooks
- DIME for non-DIET text classification models

## Limitations and Known Issues 🤏🏽
- Global Importance is disabled for REST models due to performance bottlenecks
- Explaining RASA models locally on Notebooks such as CoLab is not supported yet due to dependency issues
- Benchmark tests are in progress

📒 Docs: https://dime-xai.github.io  
📦 PyPi: https://pypi.org/project/dime-xai/1.2.1/  
🪵 Full Changelog: https://github.com/DIME-XAI/dime-xai/blob/main/CHANGELOG.md