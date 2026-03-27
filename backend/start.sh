#!/bin/bash

# \u5b89\u88c5\u4f9d\u8d56
pip install -r requirements.txt

# \u542f\u52a8\u670d\u52a1
# \u5f00\u53d1\u6a21\u5f0f\uff08\u5e26\u70ed\u91cd\u8f7d\uff09
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

# \u751f\u4ea7\u6a21\u5f0f
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
