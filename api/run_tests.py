#!/usr/bin/env python3
"""
Test runner script for the Carson API project.

This script provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n🧪 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Test runner for Carson API")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "all", "coverage", "lint"],
        help="Type of tests to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--file", "-f", help="Run specific test file")

    args = parser.parse_args()

    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]

    if args.verbose:
        base_cmd.append("-v")

    exit_code = 0

    if args.test_type == "unit":
        cmd = base_cmd + ["tests/unit/"]
        if args.file:
            cmd = base_cmd + [f"tests/unit/{args.file}"]
        exit_code = run_command(cmd, "Running unit tests")

    elif args.test_type == "integration":
        cmd = base_cmd + ["tests/integration/"]
        if args.file:
            cmd = base_cmd + [f"tests/integration/{args.file}"]
        exit_code = run_command(cmd, "Running integration tests")

    elif args.test_type == "all":
        cmd = base_cmd + ["tests/"]
        exit_code = run_command(cmd, "Running all tests")

    elif args.test_type == "coverage":
        cmd = base_cmd + [
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "tests/",
        ]
        exit_code = run_command(cmd, "Running tests with coverage")
        print("\n📊 Coverage report generated in htmlcov/index.html")

    elif args.test_type == "lint":
        # Run various linting tools if available
        tools = [
            (["python", "-m", "ruff", "check", "app/"], "Running Ruff linter"),
            (["python", "-m", "mypy", "app/"], "Running MyPy type checker"),
            (
                ["python", "-m", "black", "--check", "app/"],
                "Running Black formatter check",
            ),
        ]

        for cmd, description in tools:
            try:
                result = run_command(cmd, description)
                if result != 0:
                    exit_code = result
            except FileNotFoundError:
                print(f"⚠️  Skipping {description} - tool not installed")

    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
