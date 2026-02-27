#!/usr/bin/env python3
import sys
import os

print("🔍 ENVIRONMENT CHECK")
print("=" * 50)

# Check Python version
print(f"📌 Python version: {sys.version.split()[0]}")
print(f"📌 Python executable: {sys.executable}")

# Check if in virtual environment
in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
print(f"📌 Virtual environment: {'✅ Active' if in_venv else '❌ Not active'}")

# Check required packages
required_packages = [
    ('rich', 'rich'),
    ('tabulate', 'tabulate'),
    ('dateutil', 'python-dateutil'),
    ('pytest', 'pytest')
]

print("\n📦 CHECKING PACKAGES:")
for package_name, pip_name in required_packages:
    try:
        __import__(package_name)
        print(f"  ✅ {pip_name}")
    except ImportError:
        print(f"  ❌ {pip_name} (not installed)")

# Check directory structure
print("\n📁 CHECKING DIRECTORY STRUCTURE:")
dirs_to_check = ['models', 'utils', 'data', 'tests']
for dir_name in dirs_to_check:
    if os.path.exists(dir_name):
        print(f"  ✅ {dir_name}/")
        # Check for Python files in directories
        if dir_name in ['models', 'utils', 'tests']:
            py_files = [f for f in os.listdir(dir_name) if f.endswith('.py')]
            print(f"     Found {len(py_files)} Python files")
    else:
        print(f"  ❌ {dir_name}/ (missing)")

# Check for __init__.py files
print("\n📄 CHECKING __INIT__.PY FILES:")
init_files = ['models/__init__.py', 'utils/__init__.py', 'tests/__init__.py']
for init_file in init_files:
    if os.path.exists(init_file):
        print(f"  ✅ {init_file}")
    else:
        print(f"  ❌ {init_file} (missing)")

# Check data files
print("\n💾 CHECKING DATA FILES:")
data_files = ['users.json', 'projects.json', 'tasks.json']
for data_file in data_files:
    file_path = os.path.join('data', data_file)
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"  ✅ {data_file} ({size} bytes)")
    else:
        print(f"  ⚠️  {data_file} (will be created when needed)")

print("\n" + "=" * 50)
if in_venv and all(os.path.exists(os.path.join('data', f)) for f in data_files):
    print("✅ Environment is properly configured!")
else:
    print("⚠️  Some checks failed. Run 'pip install -r requirements.txt' if needed.")

print("=" * 50)
