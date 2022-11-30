# ingestors

``ingestors`` extract useful information from documents of different types in
a structured standard format. It retains folder structures across directories,
compressed archives and emails. The extracted data is formatted as Follow the 
Money (FtM) entities, ready for import into Aleph, or processing as an object
graph.

Supported file types:

* Plain text
* Images
* Web pages, XML documents
* PDF files
* Emails (Outlook, plain text)
* Archive files (ZIP, Rar, etc.)

Other features:

* Extendable and composable using classes and mixins.
* Generates FollowTheMoney objects to a database as result objects.
* Lightweight worker-style support for logging, failures and callbacks.
* Throughly tested.

## Development environment

For local development with a virtualenv:

```bash
python3 -mvenv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Release procedure

```bash
git pull --rebase
make test
source .env/bin/activate
bump2version {patch,minor,major} # pick the appropriate one
git push --atomic origin master $(git describe --tags --abbrev=0)
```

## Usage

Ingestors are usually called in the context of Aleph. In order to run them
stand-alone, you can use the supplied docker compose environment. To enter
a working container, run:

```bash
make build
make shell
```

Inside the shell, you will find the `ingestors` command-line tool. During
development, it is convenient to call its debug mode using files present
in the user's home directory, which is mounted at `/host`: 

```bash
ingestors debug /host/Documents/sample.xlsx
```
