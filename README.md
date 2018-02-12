# Interank

A method for predicting the success of contributions to online collaborative projects.

> Yardım, A. B., Kristof, V., Maystre, L., and Grossglauser, M., [_Can Who-Edits-What Predict Edit Survival?_](https://arxiv.org/abs/1801.04159), arXiv preprint.

## Setup

Install the `interank` library:

~~~
pip3 install -e lib
~~~

You're ready to predict some edits!

## Data

[Download the data folder](https://www.dropbox.com/sh/ltpcv16je0ps2ma/AAAUQ3ZBRLn3VxRFc3lq48gha?dl=0), containing the models' predictions and true labels, and put it in the root of the repository.

With this you can run the following notebooks:

- [frwiki-plots.ipynb](notebooks/frwiki-plots.ipynb)
- [trwiki-plots.ipynb](notebooks/trwiki-plots.ipynb)
- [linux-plots.ipynb](notebooks/linux-plots.ipynb)

For the remaining notebooks, you'll need to process the [raw data](https://dumps.wikimedia.org/backup-index.html) using the scripts in the `scripts` folder.

## Requirements

This project requires Python 3.

### Python libraries

- numpy
- scipy
- matplotlib
- scikit-learn
- jupyter
- tensorflow
- pandas
