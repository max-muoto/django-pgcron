# Contributing Guide

## Setup

Set up your development environment with:

    git clone https://github.com/max-muoto/django-pgcron.git
    cd django-cron
    make docker-setup

`make docker-setup` will set up a development environment managed by Docker. Install docker [here](https://www.docker.com/get-started) and make sure it's running.


## Documentation

[Mkdocs Material](https://squidfunk.github.io/mkdocs-material/) documentation can be built with:

    make docs

Docs can be served with:

    make docs-serve

# Linting / Style

We adhere to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) as closely as possible.

To enforce this style, we use Ruff for linting. Additionally, we ensure type correctness with Pyright.

You can run the linter with the following command:

```bash
make lint
```

To check for type correctness, use:

```bash
make type-check
```

## Releases and Versioning

The version number and release notes are manually updated by the maintainer during the release process. Do not edit these.

