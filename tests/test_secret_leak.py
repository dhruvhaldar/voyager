import subprocess
import os
import sys

def test_secret_leak_default():
    """
    Test that the API key is NOT printed by default when VOYAGER_API_KEY is missing.
    """
    env = os.environ.copy()
    # Ensure VOYAGER_API_KEY is not set
    if "VOYAGER_API_KEY" in env:
        del env["VOYAGER_API_KEY"]
    if "VOYAGER_SHOW_KEY" in env:
        del env["VOYAGER_SHOW_KEY"]

    # Add project root to PYTHONPATH so `import api.index` works
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Run a script that imports api.index
    # We use -c to run a small snippet
    result = subprocess.run(
        [sys.executable, "-c", "import api.index"],
        capture_output=True,
        text=True,
        env=env
    )

    stdout = result.stdout
    stderr = result.stderr
    combined_output = stdout + stderr

    print(f"Captured output: {combined_output}")

    # Check for the warning message (this should still be there)
    assert "SECURITY WARNING: VOYAGER_API_KEY not set." in combined_output

    # Check that the actual key is NOT leaked.
    # The current code prints: "Using generated key: <KEY>"
    # We want to ensure this specific string pattern is NOT present with a long key.
    # Or simply that "Using generated key:" is NOT followed by a 43-char string.

    # For now, let's just assert "Using generated key:" is NOT in output, assuming we change the message entirely.
    # Or better, check for the presence of the full key format.

    # We expect this assertion to FAIL before the fix.
    assert "Using generated key:" not in combined_output, "API Key leaked in logs!"

def test_secret_leak_opt_in():
    """
    Test that the API key IS printed if VOYAGER_SHOW_KEY=1 is set.
    """
    env = os.environ.copy()
    if "VOYAGER_API_KEY" in env:
        del env["VOYAGER_API_KEY"]
    env["VOYAGER_SHOW_KEY"] = "1"
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    result = subprocess.run(
        [sys.executable, "-c", "import api.index"],
        capture_output=True,
        text=True,
        env=env
    )

    combined_output = result.stdout + result.stderr

    # Should print the key when opted-in
    assert "Using generated key:" in combined_output
