# Proman Versioning

[![License](https://img.shields.io/badge/License-MPL%202.0-blue.svg)](https://spdx.org/licenses/MPL-2.0)
[![Build Status](https://travis-ci.org/kuwv/proman-versioning.svg?branch=master)](https://travis-ci.org/kuwv/proman-versioning)
[![codecov](https://codecov.io/gh/kuwv/proman-versioning/branch/master/graph/badge.svg)](https://codecov.io/gh/kuwv/proman-versioning)

## Overview

Project Manager Versioning is a PEP-440 compliant tool for automating project
versions using conventional commits.

## Install

`pip install proman-versioning`

## Setup

This tool is designed to work with any textfile using a templating pattern and
 path to the file.

### Configuring versions

Configuration can be performed with either the `.versioning` or `pyproject.toml`
files.

#### Global configuration settings:

Specific types of releases can be disabled by setting the respective release to
false.

Disable development releases:
```
enable_devreleases = false
```

Disable pre-releases:
```
enable_prereleases = false
```

Disable post-releases:
```
enable_postreleases = false
```

#### File specific settings:

Use different version compatibiliy type:
```
compat = "semver"
```

Update only the release version for a configuration:
```
release_only = true
```

#### Example `.versioning`

The `.versioning` config is a non-specfile based project file using TOML. This is the
preferred configuration for non-python projects that may use this tool.

```
[proman]
version = "1.2.3"

[proman.versioning]
disable_devreleases = true

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

#### Example `setup.cfg`

Setuptools allows `setup.cfg` to pull the version from the application. This
should be used in tandem with either of the above configurations to control
versions for a project.

```
[metadata]
name = example
version = attr: src.VERSION
...
```

## References

- https://www.conventionalcommits.org/en/v1.0.0/
- https://www.python.org/dev/peps/pep-0440/
- https://semver.org
- https://calver.org
