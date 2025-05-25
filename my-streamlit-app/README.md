# My First Streamlit App

This is a simple "Hello, World!" application built with Streamlit. It serves as a basic example of how to set up and run a Streamlit app using pyenv for Python version management and Poetry for dependency management.

## Setup Instructions

### 1. Python Environment Setup (pyenv & Python 3.11)

It's recommended to use `pyenv` to manage Python versions.

**Install pyenv:**

If you don't have `pyenv` installed, you can install it by following the official instructions. A common way is:
```bash
curl https://pyenv.run | bash
```
After installation, you'll need to add `pyenv` to your shell's startup configuration. For bash, this usually means adding the following lines to your `~/.bashrc` or `~/.zshrc` (if using zsh):

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
```
Make sure to restart your shell or source the configuration file for the changes to take effect.

**Install Python 3.11.0:**

Once `pyenv` is set up, install Python 3.11.0:
```bash
pyenv install 3.11.0
```

**Set Local Python Version:**

Navigate to the project directory (`my-streamlit-app`) and set the local Python version for this project:
```bash
cd my-streamlit-app
pyenv local 3.11.0
```
Verify the Python version:
```bash
python --version
# Should output: Python 3.11.0
```

### 2. Install Poetry

Poetry is used for dependency management. If you don't have it installed, you can install it using:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
You might need to add Poetry's bin directory to your PATH. The installer usually provides instructions for this. For example:
```bash
export PATH="/root/.local/bin:$PATH" # Adjust the path if your home directory is different
```
Verify Poetry installation:
```bash
poetry --version
```

### 3. Install Dependencies

With Poetry and the correct Python version set up, navigate to the project root (`my-streamlit-app`) and install the project dependencies:
```bash
poetry install
```
This command will create a virtual environment if one doesn't exist and install all dependencies listed in `pyproject.toml` and `poetry.lock`.

## Running the Streamlit App

After installing the dependencies, you can run the Streamlit application.

1.  **Activate the virtual environment (if not already active):**
    Poetry commands usually run within the project's virtual environment automatically. If you need to activate it manually for other purposes:
    ```bash
    poetry shell
    ```

2.  **Run the Streamlit app:**
    From the `my-streamlit-app` directory:
    ```bash
    streamlit run app.py
    ```

This will start the Streamlit development server, and your default web browser should open automatically to the app's URL (usually `http://localhost:8501`). You will see "Hello, World!" displayed on the page.
