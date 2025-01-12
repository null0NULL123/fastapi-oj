# Online Judge System

A FastAPI-based online judge system for testing.

[中文文档](README_zh.md)

## Features

- [x] User authentication
- [x] Problem listing
- [x] Code submission
- [x] Automated judging
- [ ] Leaderboard
- [ ] Frontend Style

### Code Testing

- Supports Python and C programming languages
- Real-time code execution and testing
- Multiple test cases per problem
- Time limit enforcement
- Detailed feedback on test results

## Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
uvicorn main:app --host 0.0.0.0 --port your_port --reload
```

## Project Structure

```raw
fastapi-oj/
├── .gitignore
├── main.py                  # Main application entry
├── config.py                # Configuration
├── data.csv                 # Data files
├── requirements.txt         # Project dependencies
├── assets/                  # Source images
|   ├── login.png
|   ├── home.png
├── templates/               # HTML templates
|   ├── login.html           # Login page
|   ├── home.html            # Home page
├── testcase/                # Test case files
|   ├── __init__.py
|   ├── C.json               # C programming language test cases
|   └── Python.json          # Python programming language test cases
└── utils/                   # Utility scripts
    ├── judge.py             # Code execution and judging
    └── parse.py             # Code parsing utilities and the others

```

## Display

### Login Page

![login](assets/login.png "Login Page")

### Home Page

![home](assets/home.png "Home Page")
