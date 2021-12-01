# Proman Versioning

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://spdx.org/licenses/MPL-2.0)
[![Build Status](https://travis-ci.org/kuwv/proman-versioning.svg?branch=master)](https://travis-ci.org/kuwv/proman-versioning)
[![codecov](https://codecov.io/gh/kuwv/proman-versioning/branch/master/graph/badge.svg)](https://codecov.io/gh/kuwv/proman-versioning)

## Overview

Project Manager Versioning tool is a PEP-440 compliant tool for automating
project versions using conventional commits.

## Install

`pip install proman-versioning`

## Setup

This tool is designed to work with any textfile using a templating pattern and
 path to the file.

### Configuring versioning

Release versions can be configured by choosing the types of releases to use if
any.

Disable devrelease:
```
enable_devreleases = false
```

Disable prereleases:
```
enable_prereleases = false
```

Disable postreleases:
```
enable_postreleases = false
```

#### Example `.versioning`

The `.versioning` config is a non-specfile based project file using TOML. This is the
preferred configuration for non-python projects that may use this tool.

```
[proman]
version = "1.2.3"

[proman.versioning]

[[tool.proman.versioning.files]]
filepath = "pyproject.toml"
pattern = "version = \"${version}\""

[[proman.versioning.files]]
filepath = "example/__init__.py"
pattern = "__version__ = '${version}'"
```

#### Example `pyproject.toml`

```
[tool.proman]
version = "1.2.3"

[tool.proman.versioning]

[[tool.proman.versioning.files]]
filepath = "pyproject.toml"
pattern = "version = \"${version}\""

[[tool.proman.versioning.files]]
filepath = "example/__init__.py"
pattern = "__version__ = '${version}'"
```

## References

- https://www.conventionalcommits.org/en/v1.0.0/
- https://www.python.org/dev/peps/pep-0440/
