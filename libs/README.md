# Isidro Shared Libraries

Shared libraries are used across the various Isidro microservices.  The libraries are all python3 modules.

**Note that shared libraries should not be changed to introduce any secrets, credentials, or other confidential information - the Python registry for hosting the libraries is public**

## Install required packages

```bash
apt-get install python3-venv
pip install --upgrade build keyrings.google-artifactregistry-auth twine wheel
```

## Build the libraries

Configure `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_PROJECT` environment variables, then:

```bash
python3 -m build
python3 -m twine upload --repository-url https://us-python.pkg.dev/$GOOGLE_PROJECT/isidro-libs/ dist/*
```