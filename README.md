# hackaton_MIT

## Getting Started

1. Navigate to the project directory:
    ```bash
    cd hackaton_MIT
    ```

2. Install `uv` : 
(on macOS, use Homebrew):
```bash
brew install uv
```

(on Linux, use apt or yum depending on your distribution):
```bash
# For Debian/Ubuntu-based systems
sudo apt update && sudo apt install uv

# For Red Hat/CentOS-based systems
sudo yum install uv
```

(on Windows, use Chocolatey):
```bash
choco install uv
```

3. Create the .venv
    ```bash
    uv sync
    ```

4. To add a dependency, use:
    ```bash
    uv add <dependency-name>
    ```

5. To remove a dependency, use:
    ```bash
    uv remove <dependency-name>
        ```

6. To run a Python file, use:
    ```bash
    uv run python <file-name>.py
    ```
    or  activate the virtual environment, with:
        ```bash
        source .venv/bin/activate
        ```
    (on Windows, use `. .venv\Scripts\Activate.ps1`)                 
    Once activated, you can run your Python file directly:
        ```bash
        python <file-name>.py
        ```