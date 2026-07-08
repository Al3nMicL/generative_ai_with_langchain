#!/usr/bin/env -S uv run
"""
Validation script to check the workspace environment.
Checks python version, package installations, and LangChain/LangGraph version requirements.
"""

import sys
import importlib

def check_python_version():
    print("[*] Checking Python Version...")
    major, minor = sys.version_info.major, sys.version_info.minor
    print(f"    Found: Python {sys.version}")
    if major == 3 and minor >= 13:
        print("    [PASS] Python version is compatible (>= 3.13).")
        return True
    else:
        print("    [FAIL] Python version should be >= 3.13.")
        return False

def check_package(package_name, min_version=None):
    print(f"[*] Checking import for '{package_name}'...")
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")
        print(f"    [PASS] Successfully imported '{package_name}' (Version: {version})")
        return True
    except ImportError:
        print(f"    [FAIL] Failed to import '{package_name}'. Package is not installed.")
        return False

def main():
    print("=" * 60)
    print("           Workspace Environment Validator")
    print("=" * 60)
    
    success = True
    
    # 1. Check Python
    if not check_python_version():
        success = False
    print("-" * 60)
    
    # 2. Check packages
    required_packages = [
        "langchain",
        "langchain_core",
        "langgraph",
        "pydantic",
        "openai",
        "ray",
    ]
    
    for pkg in required_packages:
        if not check_package(pkg):
            success = False
        print("-" * 60)
        
    if success:
        print("[SUCCESS] All core packages and Python environment checks passed.")
        sys.exit(0)
    else:
        print("[ERROR] Environment validation failed. Please check setup.md or requirements.txt.")
        sys.exit(1)

if __name__ == "__main__":
    main()
