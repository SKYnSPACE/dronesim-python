# dronesim-python

### Requirements

Install the following tools before moving on to the installation chapter.

- pyenv: https://github.com/pyenv/pyenv
- poetry: https://python-poetry.org/



### Installations

After you installed the requirements, run the following commands on your `workspace`:

```sh
pyenv install 3.11.3
pyenv global 3.11.3

git clone "https://github.com/SKYnSPACE/dronesim-python"
cd ./dronesim-python

poetry install
```



### How to use

Suppose `{$workspace}` is the folder where you cloned the git repository.

```sh
cd {$workspace}/dronesim-python/dronesim_python

poetry shell
python main.py
```

