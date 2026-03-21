# Documentation Internationalization (i18n)

This directory contains translation files for the pyvista-js documentation using the Sphinx i18n feature.

## Overview

The internationalization system uses:

- **Sphinx gettext builder** to extract translatable strings into `.pot` (Portable Object Template) files
- **sphinx-intl** to manage translation catalogs and create `.po` (Portable Object) files for each language
- **gettext** to compile `.po` files into binary `.mo` (Machine Object) files used by Sphinx

## Workflow for Translators

### 1. Extract Translatable Strings

First, generate the message catalogs (`.pot` files) from the documentation source:

```bash
cd docs
make gettext
```

This creates `.pot` files in `docs/_build/gettext/` containing all translatable strings.

### 2. Create or Update Translation Files

For a new language (e.g., Japanese - `ja`):

```bash
cd docs
make update-po LANG=ja
```

Or using sphinx-intl directly:

```bash
sphinx-intl update -p _build/gettext -l ja
```

This creates/updates `.po` files in `docs/locale/ja/LC_MESSAGES/`.

### 3. Translate the Strings

Edit the `.po` files in `docs/locale/<language>/LC_MESSAGES/` and fill in the translations:

```po
#: ../../index.md:53
msgid "Installation"
msgstr "インストール"

#: ../../index.md:53
msgid "Getting Started"
msgstr "はじめに"
```

### 4. Build Translated Documentation

Build the documentation in the target language:

```bash
cd docs
make html-lang LANG=ja
```

Or using sphinx-build directly:

```bash
sphinx-build -b html -D language=ja . _build/html/ja
```

The translated documentation will be in `docs/_build/html/ja/`.

## Directory Structure

```
docs/
├── locale/                          # Translation directory
│   ├── ja/                          # Japanese translations
│   │   └── LC_MESSAGES/
│   │       ├── index.po            # Main page translations
│   │       ├── api/
│   │       ├── tutorials/
│   │       ├── howtos/
│   │       └── explanation/
│   └── <other_languages>/          # Other language translations
├── _build/
│   └── gettext/                    # Generated .pot files (not committed)
│       ├── index.pot
│       └── ...
└── conf.py                         # Sphinx configuration with i18n settings

```

## Configuration

The i18n configuration in `docs/conf.py`:

```python
language = "en"  # Default language
locale_dirs = ["locale/"]  # Translation directory
gettext_compact = False  # One .po file per document
```

## Supported Languages

Currently supported languages:

- English (`en`) - default
- Japanese (`ja`) - example

To add a new language, follow the workflow above with the appropriate language code.

## Continuous Integration

The `.github/workflows/build-i18n-docs.yml` workflow automatically builds documentation for all supported languages on every push to ensure translations don't break the build.

## Resources

- [Sphinx Internationalization](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html)
- [sphinx-intl Documentation](https://sphinx-intl.readthedocs.io/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)
