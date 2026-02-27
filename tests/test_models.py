import pytest
import json
import os
from datetime import datetime, timedelta
from models import User, Project, Task
from utils.file_handler import FileHandler

class TestUser:
    """Test cases for User model."""
    
    def setup_method(self):
        """Reset class state before each test."""
        User._all_users.clear()
        User._next_id = 1
    
    def test_user_creation(self):
        """Test creating a user."""
        user = User("John Doe", "john@example.com")
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.user_id == 1
        assert user.projects == []
    
    def test_user_validation(self):
        """Test user validation."""
        user = User("John Doe", "john@example.com")
        
        # Test name validation
        with pytest.raises(ValueError):
            user.name = "A"
        
        with pytest.raises(ValueError):
            user.name = ""
        
        # Test email validation
        with pytest.raises(ValueError):
            user.email = "invalid-email"
        
        with pytest.raises(ValueError):
            user.email = "noatsign.com"
    
    def test_find_by_name(self):
        """Test finding users by name."""
        User("John Doe", "john@example.com")
        User("Jane Smith", "jane@example.com")
        User("John Smith", "john.smith@example.com")
        
        results = User.find_by_name("john")
        assert len(results) == 2
        assert all("john" in u.name.lower() for u in results)
    
    def test_add_remove_project(self):
        """Test adding and removing projects from user."""
        user = User("John Doe", "john@example.com")
        
        user.add_project(1)
        assert 1 in user.projects
        
        user.add_project(1)  # Duplicate
        assert len(user.projects) == 1
        
        user.remove_project(1)
        assert 1 not in user.projects
    
    def test_to_dict_from_dict(self):
        """Test serialization and deserialization."""
        original = User("John Doe", "john@example.com")
        data = original.to_dict()
        
        restored = User.from_dict(data)
        assert restored.name == original.name
        assert restored.email == original.email
        assert restored.user_id == original.user_id

class TestProject:
    """Test cases for Project model."""
    
    def setup_method(self):
        """Reset class state before each test."""
        Project._all_projects.clear()
        Project._next_id = 1
        User._all_users.clear()
        User._next_id = 1
    
    def test_project_creation(self):
        """Test creating a project."""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        project = Project("Test Project", "A test project", due_date, 1)
        
        assert project.title == "Test Project"
        assert project.description == "A test project"
        assert project.user_id == 1
        assert project.tasks == []
        assert not project.is_overdue
    
    def test_project_validation(self):
        """Test project validation."""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        project = Project("Test Project", "", due_date, 1)
        
        with pytest.raises(ValueError):
            project.title = ""
        
        with pytest.raises(ValueError):
            project.due_date = "invalid-date"
    
    def test_overdue_check(self):
        """Test overdue project detection."""
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        
        overdue_project = Project("Overdue", "", past_date, 1)
        assert overdue_project.is_overdue
        
        future_project = Project("Future", "", future_date, 1)
        assert not future_project.is_overdue
    
    def test_find_by_user(self):
        """Test finding projects by user."""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        Project("Project 1", "", due_date, 1)
        Project("Project 2", "", due_date, 1)
        Project("Project 3", "", due_date, 2)
        
        user1_projects = Project.find_by_user(1)
        assert len(user1_projects) == 2
        
        user2_projects = Project.find_by_user(2)
        assert len(user2_projects) == 1
    
    def test_add_remove_task(self):
        """Test adding and removing tasks from project."""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        project = Project("Test Project", "", due_date, 1)
        
        project.add_task(1)
        assert 1 in project.tasks
        
        project.add_task(1)  # Duplicate
        assert len(project.tasks) == 1
        
        project.remove_task(1)
        assert 1 not in project.tasks

class TestTask:
    """Test cases for Task model."""
    
    def setup_method(self):
        """Reset class state before each test."""
        Task._all_tasks.clear()
        Task._next_id = 1
    
    def test_task_creation(self):
        """Test creating a task."""
        task = Task("Test Task", "A test task", 1)
        
        assert task.title == "Test Task"
        assert task.description == "A test task"
        assert task.project_id == 1
        assert task.status == "pending"
        assert task.assigned_users == []
        assert not task.is_completed
    
    def test_task_validation(self):
        """Test task validation."""
        task = Task("Test Task", "", 1)
        
        with pytest.raises(ValueError):
            task.title = ""
        
        with pytest.raises(ValueError):
            task.status = "invalid"
    
    def test_status_transitions(self):
        """Test task status changes."""
        task = Task("Test Task", "", 1)
        
        assert task.status == "pending"
        
        task.status = "in_progress"
        assert task.status == "in_progress"
        
        task.mark_complete()
        assert task.status == "completed"
        assert task.is_completed
    
    def test_find_by_project(self):
        """Test finding tasks by project."""
        Task("Task 1", "", 1)
        Task("Task 2", "", 1)
        Task("Task 3", "", 2)
        
        project1_tasks = Task.find_by_project(1)
        assert len(project1_tasks) == 2
        
        project2_tasks = Task.find_by_project(2)
        assert len(project2_tasks) == 1
    
    def test_assign_unassign_user(self):
        """Test assigning and unassigning users to task."""
        task = Task("Test Task", "", 1)
        
        task.assign_user(1)
        assert 1 in task.assigned_users
        
        task.assign_user(1)  # Duplicate
        assert len(task.assigned_users) == 1
        
        task.assign_user(2)
        assert len(task.assigned_users) == 2
        
        task.unassign_user(1)
        assert 1 not in task.assigned_users
        assert 2 in task.assigned_users

class TestFileHandler:
    """Test cases for FileHandler utility."""
    
    def setup_method(self):
        """Ensure clean state before each test."""
        # Create data directory if it doesn't exist
        if not os.path.exists(FileHandler.DATA_DIR):
            os.makedirs(FileHandler.DATA_DIR)
    
    def teardown_method(self):
        """Clean up after each test."""
        # Remove test files
        test_file = FileHandler.get_file_path('test.json')
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_save_and_load(self):
        """Test saving and loading data."""
        data = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test 2"}]
        
        # Save data
        result = FileHandler.save_data('test.json', data)
        assert result == True
        
        # Load data
        loaded = FileHandler.load_data('test.json')
        assert loaded == data
    
    def test_load_nonexistent(self):
        """Test loading nonexistent file."""
        data = FileHandler.load_data('nonexistent.json')
        assert data == []
    
    def test_backup(self):
        """Test creating backup."""
        # First save some data
        data = [{"id": 1, "name": "Test"}]
        FileHandler.save_data('test.json', data)
        
        # Create backup
        backup_name = FileHandler.backup_data('test.json')
        assert backup_name is not None
        
        # Verify backup exists
        backup_path = FileHandler.get_file_path(backup_name)
        assert os.path.exists(backup_path)
        
        # Clean up backup
        if os.path.exists(backup_path):
            os.remove(backup_path)