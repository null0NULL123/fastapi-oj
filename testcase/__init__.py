import json

test_cases = {}
with open("testcase/C.json", "r") as c, open("testcase/Python.json", "r") as python:
    test_cases["C"] = json.load(c)
    test_cases["Python"] = json.load(python)
