#!/bin/bash
cd "$(dirname "$0")"
cd src
rm ../deployable.zip
zip ../deployable.zip -r * -x '*__pycache__*'