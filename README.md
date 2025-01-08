
# Reviewer: Automated Code Review with OpenAI

**Reviewer** is a Python tool designed to analyze code changes using OpenAI's language models. It provides suggestions for improving your code, identifying potential issues, and ensuring code quality.

## Features
- **Pre-commit Hook**: Analyze staged changes before committing them.
- **GitHub Pull Request Integration**: Review PRs directly by providing the URL.
- **Customizable Exclusions**: Filter out specific file types (e.g., images, binary files).
- **Seamless OpenAI Integration**: Uses OpenAI API for code review suggestions.

## Installation

### 1. Clone the repository:
```bash
git clone https://github.com/your_username/reviewer.git
cd reviewer
```

### 2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables Setup
Reviewer requires the following environment variables to function properly:

- **OpenAI API Key**: To access OpenAI's API.
  
  Set the \`OPENAI_API_KEY\` environment variable to your OpenAI API key.
  ```bash
  export OPENAI_API_KEY="your_openai_api_key"
  ```

- **GitHub Personal Access Token (Optional)**: To access private GitHub repositories or rate-limit-free API requests.
  
  Set the \`GITHUB_TOKEN\` environment variable to your GitHub personal access token.
  ```bash
  export GITHUB_TOKEN="your_github_personal_access_token"
  ```
  You can generate a GitHub personal access token from GitHub Settings.

### Persistent Setup (Optional)
To persist the environment variables across terminal sessions, add the export lines to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`, etc.):
```bash
echo 'export OPENAI_API_KEY="your_openai_api_key"' >> ~/.bashrc
echo 'export GITHUB_TOKEN="your_github_personal_access_token"' >> ~/.bashrc
```

## Usage

### 1. Standalone Mode
Run the reviewer on unstaged changes in your local repository:
```bash
python reviewer.py
```

### 2. Pre-commit Hook
Add the following script to \`.git/hooks/pre-commit\`:
```bash
#!/bin/bash
python path/to/reviewer.py --pre-commit
```
Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```
From now on, every time you try to commit changes, Reviewer will analyze the staged changes before the commit is finalized.

### 3. GitHub Pull Request Review
Analyze a GitHub pull request by providing its URL:
```bash
python reviewer.py --url https://github.com/<org>/<repo>/pull/<pr_number>
```

## Customization

### Excluded File Types
You can customize the excluded file types by editing the \`EXCLUDED_EXTENSIONS\` list in the \`reviewer.py\` file. For example:
```python
EXCLUDED_EXTENSIONS = [
    ".pbxproj",
    ".storyboard",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
]
```
Add or remove extensions as needed to match your project's requirements.

## Contributing
Contributions are welcome! If you'd like to contribute, please fork the repository, create a feature branch, and submit a pull request.

## License
This project is licensed under the MIT License.
