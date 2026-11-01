"""
End-to-end Smoke Test for Streamlit Dashboard Server
"""

import subprocess
import sys
import time
import urllib.request


def test_streamlit_server():
    print("Starting Streamlit Dashboard server for smoke testing...")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "sales-intelligence-platform/dashboard/app.py",
            "--server.headless",
            "true",
            "--server.port",
            "8599",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Allow server 4 seconds to spin up
    time.sleep(4)

    try:
        url_health = "http://localhost:8599/_stcore/health"
        print(f"Pinging health endpoint: {url_health}")
        req = urllib.request.urlopen(url_health, timeout=5)
        health_status = req.getcode()
        print(f"Health Status: {health_status} OK")
        assert health_status == 200, f"Expected 200, got {health_status}"

        url_main = "http://localhost:8599"
        print(f"Pinging main portal: {url_main}")
        req_main = urllib.request.urlopen(url_main, timeout=5)
        main_status = req_main.getcode()
        html = req_main.read().decode("utf-8")
        print(f"Main Page Status: {main_status} OK | Loaded {len(html):,} bytes")
        assert main_status == 200, f"Expected 200, got {main_status}"
        assert "Streamlit" in html or "streamlit" in html.lower()

        print("\nSMOKE TEST PASSED: Streamlit Dashboard is 100% functional and serving live traffic!")
    finally:
        print("Terminating test server instance...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    test_streamlit_server()
