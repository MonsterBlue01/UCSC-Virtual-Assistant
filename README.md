# SchoolBot

## Set up virtual environment

In order to run this project, you need to first create and activate a virtual environment. This helps you manage dependencies and keep your project environment clean.

### Create a virtual environment

In the project root directory, run the following command to create a virtual environment named `mybotenv`:

```bash
python3 -m venv mybotenv
```

### Activate virtual environment

After creating the virtual environment, you need to activate it. In the project root directory, run the following command:

```bash
source mybotenv/bin/activate
```

### Install dependencies

Once the virtual environment is activated, install the project dependencies by running:

```bash
pip install -r requirements.txt
```

This command will install all the necessary packages as specified in the `requirements.txt` file.

### Update dependencies

To update the `requirements.txt` file with the latest packages from your virtual environment, run:

```bash
pip freeze > requirements.txt
```

This will generate a new `requirements.txt` file with a list of all installed packages and their versions.

### Exit the virtual environment

When you are done working and want to exit the virtual environment, just run the following command in the terminal:

```bash
deactivate
```