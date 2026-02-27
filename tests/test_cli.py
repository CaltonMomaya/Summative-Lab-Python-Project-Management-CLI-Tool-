import pytest
from unittest.mock import Mock, patch, MagicMock
from main import ProjectManagementCLI
from models import User, Project, Task

class TestCLI:
    """Test cases for CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = ProjectManagementCLI()
        
        # Reset class state
        User._all_users.clear()
        User._next_id = 1
        Project._all_projects.clear()
        Project._next_id = 1
        Task._all_tasks.clear()
        Task._next_id = 1
    
    def create_mock_args(self, **kwargs):
        """Create mock arguments object."""
        args = Mock()
        for key, value in kwargs.items():
            setattr(args, key, value)
        return args
    
    def test_add_user_command(self):
        """Test add-user command."""
        args = self.create_mock_args(name="John Doe", email="john@example.com")
        
        with patch('main.print_success') as mock_success:
            self.cli.add_user(args)
            
            # Verify user was created
            users = User.get_all()
            assert len(users) == 1
            assert users[0].name == "John Doe"
            assert users[0].email == "john@example.com"
            
            mock_success.assert_called_once()
    
    def test_add_user_invalid_email(self):
        """Test add-user with invalid email."""
        args = self.create_mock_args(name="John Doe", email="invalid-email")
        
        with patch('main.print_error') as mock_error:
            self.cli.add_user(args)
            
            # Verify no user was created
            assert len(User.get_all()) == 0
            mock_error.assert_called_once()
    
    def test_add_project_command(self):
        """Test add-project command."""
        # First create a user
        user = User.create("John Doe", "john@example.com")
        
        args = self.create_mock_args(
            user="John Doe",
            title="Test Project",
            description="A test project",
            due_date="2024-12-31"
        )
        
        with patch('main.print_success') as mock_success:
            self.cli.add_project(args)
            
            # Verify project was created
            projects = Project.get_all()
            assert len(projects) == 1
            assert projects[0].title == "Test Project"
            assert projects[0].user_id == user.user_id
            
            # Verify user has project
            assert user.projects == [projects[0].project_id]
            
            mock_success.assert_called_once()
    
    def test_add_project_user_not_found(self):
        """Test add-project with non-existent user."""
        args = self.create_mock_args(
            user="Nonexistent User",
            title="Test Project",
            description="A test project",
            due_date="2024-12-31"
        )
        
        with patch('main.print_error') as mock_error:
            self.cli.add_project(args)
            
            # Verify no project was created
            assert len(Project.get_all()) == 0
            mock_error.assert_called_once()
    
    def test_add_task_command(self):
        """Test add-task command."""
        # Create user and project
        user = User.create("John Doe", "john@example.com")
        project = Project.create("Test Project", "", "2024-12-31", user.user_id)
        user.add_project(project.project_id)
        
        args = self.create_mock_args(
            project="Test Project",
            title="Test Task",
            description="A test task",
            assign=None
        )
        
        with patch('main.print_success') as mock_success:
            self.cli.add_task(args)
            
            # Verify task was created
            tasks = Task.get_all()
            assert len(tasks) == 1
            assert tasks[0].title == "Test Task"
            assert tasks[0].project_id == project.project_id
            
            # Verify project has task
            assert project.tasks == [tasks[0].task_id]
            
            mock_success.assert_called_once()
    
    def test_complete_task_command(self):
        """Test complete-task command."""
        # Create task
        task = Task.create("Test Task", "", 1)
        
        args = self.create_mock_args(task_id=task.task_id)
        
        with patch('main.print_success') as mock_success:
            self.cli.complete_task(args)
            
            # Verify task is completed
            assert task.is_completed
            mock_success.assert_called_once()
    
    def test_assign_task_command(self):
        """Test assign-task command."""
        # Create user and task
        user = User.create("John Doe", "john@example.com")
        task = Task.create("Test Task", "", 1)
        
        args = self.create_mock_args(task_id=task.task_id, user="John Doe")
        
        with patch('main.print_success') as mock_success:
            self.cli.assign_task(args)
            
            # Verify user is assigned
            assert user.user_id in task.assigned_users
            mock_success.assert_called_once()
    
    def test_list_users_command(self):
        """Test list-users command."""
        # Create some users
        User.create("John Doe", "john@example.com")
        User.create("Jane Smith", "jane@example.com")
        
        args = self.create_mock_args(name=None)
        
        with patch('main.display_users_table') as mock_display:
            self.cli.list_users(args)
            
            # Verify display was called with all users
            mock_display.assert_called_once()
            users_arg = mock_display.call_args[0][0]
            assert len(users_arg) == 2
    
    def test_list_users_filtered(self):
        """Test list-users with name filter."""
        # Create some users
        User.create("John Doe", "john@example.com")
        User.create("Jane Smith", "jane@example.com")
        User.create("John Smith", "john.smith@example.com")
        
        args = self.create_mock_args(name="john")
        
        with patch('main.display_users_table') as mock_display:
            self.cli.list_users(args)
            
            # Verify filtered display
            users_arg = mock_display.call_args[0][0]
            assert len(users_arg) == 2
            assert all("john" in u.name.lower() for u in users_arg)
    
    def test_search_command(self):
        """Test search command."""
        # Create test data
        user = User.create("John Doe", "john@example.com")
        project = Project.create("Test Project", "A test project", "2024-12-31", user.user_id)
        task = Task.create("Test Task", "A test task", project.project_id)
        
        args = self.create_mock_args(query="test")
        
        with patch('main.print_info') as mock_info:
            self.cli.search(args)
            
            # Verify search found items
            assert mock_info.call_count >= 3  # Should show users, projects, and tasks
    
    def test_find_user_helper(self):
        """Test _find_user helper method."""
        # Create user
        user = User.create("John Doe", "john@example.com")
        
        # Find by ID
        found = self.cli._find_user(str(user.user_id))
        assert found == user
        
        # Find by name
        found = self.cli._find_user("John Doe")
        assert found == user
        
        # Find non-existent
        found = self.cli._find_user("Nonexistent")
        assert found is None
    
    def test_find_project_helper(self):
        """Test _find_project helper method."""
        # Create user and project
        user = User.create("John Doe", "john@example.com")
        project = Project.create("Test Project", "", "2024-12-31", user.user_id)
        
        # Find by ID
        found = self.cli._find_project(str(project.project_id))
        assert found == project
        
        # Find by title
        found = self.cli._find_project("Test Project")
        assert found == project
        
        # Find non-existent
        found = self.cli._find_project("Nonexistent")
        assert found is None
    
    @patch('main.ProjectManagementCLI.save_data')
    def test_data_persistence(self, mock_save):
        """Test that data is saved after commands."""
        # Mock the save method
        self.cli.save_data = mock_save
        
        # Run a command that modifies data
        args = self.create_mock_args(name="John Doe", email="john@example.com")
        self.cli.add_user(args)
        
        # Verify save was called
        mock_save.assert_called_once()