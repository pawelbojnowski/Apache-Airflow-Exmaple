#!/bin/bash
set -e

VENV=.venv
$VENV/bin/pytest -v
