# TaxForce Dashboard

## Getting Started

To ensure a consistent environment, we recommend using `uv` to manage dependencies.

> [!IMPORTANT]
> **Version Consistency is Critical**
> The dashboard's layout and functionality (especially Streamlit components) can vary significantly between versions. To reproduce the intended user experience and results, it is essential to use the exact package versions specified in `requirements.txt`. **Using a virtual environment is highly recommended to ensure these versions match exactly.**

### Prerequisites

- Python 3 (specifically 3.10.12 is recommended)
- [`uv`](https://github.com/astral-sh/uv)

### Installation

1. **Create a virtual environment:**
   ```bash
   uv venv
   ```

2. **Activate the environment:**
   ```bash
   source .venv/bin/activate
   # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

### Running the Dashboard

Launch the dashboard application:
```bash
python3 run_dashboard.py
```

### Troubleshooting

**Compatibility Issues / Python Version**

This project is built and tested with **Python 3.10.12**. If you encounter issues, please try using this exact version. You can easily install and use it with `uv`:

```bash
# Install the specific python version
uv python install 3.10.12

# Re-create the virtual environment using this version
uv venv --python 3.10.12
```
Then proceed with activating the environment and installing dependencies as described above.
