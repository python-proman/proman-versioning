# Proman Versioning

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://spdx.org/licenses/MPL-2.0)
[![Build Status](https://travis-ci.org/kuwv/proman-versioning.svg?branch=master)](https://travis-ci.org/kuwv/proman-versioning)
[![codecov](https://codecov.io/gh/kuwv/proman-versioning/branch/master/graph/badge.svg)](https://codecov.io/gh/kuwv/proman-versioning)

## Overview

Project Manager Versioning tool.

## Install

`pip install proman-versioning`

## Setup

```
[tool.proman.versioning]
enable_devreleases = true
enable_prereleases = true
enable_postreleases = true

[[tool.proman.versioning.files]]
filepath = "example/__init__.py"
pattern = "__version__ = '${version}'"

[[tool.proman.versioning.files]]
filepath = "pyproject.toml"
pattern = "version = \"${version}\""
```
