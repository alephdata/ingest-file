# ingestors

:warning: PROJECT STATUS: SUNSETTING :warning:
Our involvement with this open-source project is being sunsetted. Maintenance of this version will officially end after December 2025.

**Why?**

This decision marks a significant strategic shift for us. Over the past year, our team has completely rewritten the Aleph codebase from scratch to launch Aleph Pro. As we transition to this new supported platform, we are focusing our resources entirely on Aleph Pro to ensure we can keep the lights on for investigations around the world.

For further details on this decision and what it means for the future, please read our `official FAQs <https://www.occrp.org/en/announcement/aleph-pro-frequently-asked-questions-on-the-future-of-occrps-investigative-data-platform/>`__ .

**Timeline & Support**

- We will continue to provide maintenance for this repository until December 31st, 2025. After this date, no further updates, bug fixes, or support will be provided by the core team.
- For any questions regarding the transition or the legacy software, please reach out via our `Discourse community <https://aleph.discourse.group//>`__.
- For those currently hosting their own Aleph instances, we will be in touch with you very soon regarding the transition.
- Organizations and individuals looking to collaborate can reach out to aleph-pro@occrp.org.

**Thank you!**
We are incredibly proud of what we’ve built so far. Thank you to all the contributors and community members who helped build this project and believed in our mission.


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
make build
make test
source .env/bin/activate
bump2version {patch,minor,major} # pick the appropriate one
git push --atomic origin $(git branch --show-current) $(git describe --tags --abbrev=0)
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

## License

As of release version 3.18.4 `ingest-file` is licensed under the AGPLv3 or later license. Previous versions were released under the MIT license.
