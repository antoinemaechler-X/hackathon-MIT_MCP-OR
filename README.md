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