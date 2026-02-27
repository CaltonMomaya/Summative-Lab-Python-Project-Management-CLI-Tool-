#!/usr/bin/env python3
"""
Quick test to verify all components are working.
Run with: python quick_test.py
"""

def run_test(name, func):
    """Run a test function and print result."""
    try:
        print(f"Testing {name}... ", end="")
        func()
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_imports():
    """Test that all modules can be imported."""
    import models
    import utils
    from models import User, Project, Task
    from utils import file_handler, helpers
    print("✓ Imports successful", end="")

def test_file_handler():
    """Test file handler functionality."""
    from utils.file_handler import FileHandler
    FileHandler.ensure_data_dir()
    test_data = [{"test": "data"}]
    FileHandler.save_data("test.json", test_data)
    loaded = FileHandler.load_data("test.json")
    assert loaded == test_data
    import os
    os.remove(FileHandler.get_file_path("test.json"))
    print("✓ File handler works", end="")

def test_user_model():
    """Test user model."""
    from models.user import User
    # Reset state
    User._all_users.clear()
    User._next_id = 1
    
    user = User("Test User", "test@example.com")
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.user_id == 1
    print("✓ User model works", end="")

def test_project_model():
    """Test project model."""
    from models.project import Project
    # Reset state
    Project._all_projects.clear()
    Project._next_id = 1
    
    project = Project("Test Project", "Description", "2025-12-31", 1)
    assert project.title == "Test Project"
    assert project.user_id == 1
    print("✓ Project model works", end="")

def test_task_model():
    """Test task model."""
    from models.task import Task
    # Reset state
    Task._all_tasks.clear()
    Task._next_id = 1
    
    task = Task("Test Task", "Description", 1)
    assert task.title == "Test Task"
    assert task.status == "pending"
    task.mark_complete()
    assert task.is_completed
    print("✓ Task model works", end="")

def test_cli_commands():
    """Test that CLI commands can be imported."""
    import main
    print("✓ CLI main module works", end="")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 QUICK TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("File Handler", test_file_handler),
        ("User Model", test_user_model),
        ("Project Model", test_project_model),
        ("Task Model", test_task_model),
        ("CLI Module", test_cli_commands),
    ]
    
    passed = 0
    for name, func in tests:
        if run_test(name, func):
            passed += 1
    
    print("=" * 50)
    print(f"📊 RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 50)
    
    if passed == len(tests):
        print("🎉 All systems go! Your project is ready to use!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
