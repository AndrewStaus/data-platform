# .mkdocs/

Configuration files and potentially other assets related to the MkDocs documentation
site for this project.

## Purpose

- **Centralized Configuration:** All MkDocs-specific settings are managed within this
directory, keeping the project's documentation setup organized.
- **Theme Customization:** If the Material for MkDocs theme is used, this directory can
house custom overrides to tailor the look and feel of the documentation site.

## Contents

- `mkdocs.yml`: The main configuration file for MkDocs, defining site settings, 
navigation structure, theme, and extensions.
- `docs/`: A directory containing md files that are converted to static pages on the doc
site.
- `make_stubs.py` A script that will iterate through the project source code and
create documentation stubs that will be rendered in the page.

## Usage

Running `mkdocs serve` will create a local copy of the site documents for review.
Published documentation will automatically be generated when code is merged to the main
git branch.