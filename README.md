# Proman Releases

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://spdx.org/licenses/Apache-2.0)
[![Build Status](https://travis-ci.org/kuwv/proman-releases.svg?branch=master)](https://travis-ci.org/kuwv/proman-releases)
[![codecov](https://codecov.io/gh/kuwv/proman-releases/branch/master/graph/badge.svg)](https://codecov.io/gh/kuwv/proman-releases)

## Overview

Project Manager Versioning tool.

## Install

`pip install proman_versions`

## Setup

```
[tool.proman.release]
enable_devreleases = true
enable_prereleases = true
enable_postreleases = true

[[tool.proman.release.files]]
filepath = "example/__init__.py"
pattern = "__version__ = '${version}'"

[[tool.proman.release.files]]
filepath = "pyproject.toml"
pattern = "version = \"${version}\""
```
