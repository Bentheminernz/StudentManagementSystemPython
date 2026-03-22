# Student Management System

This is my submission for the NZQA Level 3 Digital Technologies AS91906 standard.

## Prerequisites
Before starting make sure you have the following installed:
- [uv](https://github.com/astral-sh/uv#installation) for Python dependency management 

### 1. Clone the Repository
```bash
git clone https://github.com/Bentheminernz/StudentManagementSystemPython
cd StudentManagementSystemPython
```

### 2. Install the dependencies
```bash
uv sync
```

### 3. Run the program
```bash
uv run main.py
```

## Contributor Guide
For contributing please install the Git Pre Commit Hooks using this command
```bash
uv run pre-commit install
```
This makes it so when you go to commit it'll format and lint the codebase. It'll also run the tests.

You can manually run the tests using:
```bash
uv run pytest
```