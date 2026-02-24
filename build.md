# Build and Development Guide

This guide provides instructions for setting up, running, and testing the Voyager satellite emulator locally.

## Prerequisites

- **Python 3.8+**: Ensure you have Python installed. You can check with `python --version`.
- **Git**: To clone and manage the repository.

## Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dhruvhaldar/voyager.git
   cd voyager
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```powershell
     .\venv\Scripts\activate.ps1
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

Voyager serves both the backend API and the static frontend from a single server.

### Start the Voyager Server

Run the development server using Uvicorn:

```bash
uvicorn api.index:app --reload
```

- **Frontend**: Visit `http://localhost:8000` to access the Avionics Dashboard.
- **API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs.

## Testing

Voyager uses `pytest` for automated testing.

### Run All Tests
```bash
pytest
```

> [!TIP]
> If the `pytest` command is not found in your terminal, try running it as a module: `python -m pytest`.

### Run Specific Test Categories
- **Unit Tests**: `pytest tests/unit/`
- **E2E Tests**: `pytest tests/e2e/`
- **Security Tests**: `pytest tests/test_security_headers.py`

### Vercel (Recommended)

The project is configured for Vercel out of the box (`vercel.json`).

1. Install the Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project root.
3. Follow the prompts to deploy.
