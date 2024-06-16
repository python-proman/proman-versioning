# Proman Versioning

[![License](https://img.shields.io/badge/License-LGPL%203.0-blue.svg)](https://spdx.org/licenses/LGPL-3.0)
![Build Status](https://github.com/python-proman/proman-versioning/actions/workflows/ci.yml/badge.svg)
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

#### Example `.version` configuration

The `.versioning` config is a non-specfile based project file using TOML. This
is the preferred configuration for non-python projects that may use this tool.

<!--
Default versioning compatibility for `.version` files is semantic versioning
(`semver`).
-->
```
version = "1.2.3"

[[versioning.files]]
filepath = "example/__init__.py"
pattern = "__version__ = '${version}'"

[[versioning.files]]
filepath = "chart/Chart.yaml"
patterns = [
  "version = \"${version}\"",
  "appVersion = \"${version}\""
]
```

#### Example `pyproject.toml`

<!--
Default versioning compatibility for `pyproject.toml` is PEP440 (`pep440`).
-->
```
[project]
name = "example"
version = "1.2.3"

[tool.proman.versioning]
compat = "semver"

[[tool.proman.versioning.files]]
filepath = "example/__init__.py"
pattern = "__version__ = '${version}'"

[[tool.proman.versioning.files]]
filepath = "chart/Chart.yaml"
patterns = [
  "version = \"${version}\"",
  "appVersion = \"${version}\""
]
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
