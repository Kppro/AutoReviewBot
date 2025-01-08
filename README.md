# Reviewer: Automated Code Review with OpenAI

Reviewer is a Python tool designed to analyze code changes using OpenAI's language models. 
It provides suggestions for improving your code, identifying potential issues, and ensuring code quality.

## Features

- **Pre-commit Hook**: Analyze staged changes before committing them.
- **GitHub Pull Request Integration**: Review PRs directly by providing the URL.
- **Customizable Exclusions**: Filter out specific file types (e.g., images, binary files).
- **Seamless OpenAI Integration**: Uses OpenAI API for code review suggestions.

## Installation

### 1. Clone the repository:

   ```
   git clone https://github.com/your_username/reviewer.git
   cd reviewer
   ```

### 2. Create a virtual env and install dependencies

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Usage

### 1. Standalone Mode

    python reviewer.py

### 2. Pre-commit Hook

1. Add the following to .git/hooks/pre-commit

    ```
    #!/bin/bash
    reviewer.py --pre-commit
    ```

2. Make it executable

    ```
    chmod +x .git/hooks/pre-commit
    ```

    
### 3. GitHub Pull Request Review

    ```
    python reviewer.py --url https://github.com/<org>/<repo>/pull/<pr_number>
    ```

    
