from typing import List, Optional, Dict, Any
from datetime import datetime
from dateutil import parser
from utils.file_handler import FileHandler

class Project:
    """
    Project class representing a project in the system.
    
    Attributes:
        project_id (int): Unique identifier for the project
        title (str): Project title
        description (str): Project description
        due_date (datetime): Project due date
        user_id (int): ID of user who owns this project
        tasks (List[int]): List of task IDs belonging to project
        created_at (str): Timestamp when project was created
    """
    
    # Class attribute to track all projects
    _all_projects: Dict[int, 'Project'] = {}
    _next_id: int = 1
    
    def __init__(self, title: str, description: str, due_date: str, user_id: int,
                 project_id: Optional[int] = None, tasks: Optional[List[int]] = None,
                 created_at: Optional[str] = None):
        """
        Initialize a new Project instance.
        
        Args:
            title: Project title
            description: Project description
            due_date: Project due date (ISO format string)
            user_id: ID of user who owns this project
            project_id: Optional project ID (auto-generated if not provided)
            tasks: Optional list of task IDs
            created_at: Optional creation timestamp
        """
        self.project_id = project_id or Project._get_next_id()
        self._title = title
        self._description = description
        self._due_date = parser.parse(due_date) if isinstance(due_date, str) else due_date
        self.user_id = user_id
        self.tasks = tasks or []
        self.created_at = created_at or datetime.now().isoformat()
        
        # Add to class registry
        Project._all_projects[self.project_id] = self
    
    @property
    def title(self) -> str:
        """Get project title."""
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        """
        Set project title with validation.
        
        Args:
            value: New title value
            
        Raises:
            ValueError: If title is empty
        """
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        self._title = value.strip()
    
    @property
    def description(self) -> str:
        """Get project description."""
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        """Set project description."""
        self._description = value.strip() if value else ""
    
    @property
    def due_date(self) -> datetime:
        """Get project due date."""
        return self._due_date
    
    @due_date.setter
    def due_date(self, value: str) -> None:
        """
        Set project due date.
        
        Args:
            value: Due date string
            
        Raises:
            ValueError: If date format is invalid
        """
        try:
            self._due_date = parser.parse(value)
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue."""
        return datetime.now() > self._due_date
    
    @classmethod
    def _get_next_id(cls) -> int:
        """Get the next available project ID."""
        current_id = cls._next_id
        cls._next_id += 1
        return current_id
    
    @classmethod
    def create(cls, title: str, description: str, due_date: str, user_id: int) -> 'Project':
        """
        Factory method to create a new project.
        
        Args:
            title: Project title
            description: Project description
            due_date: Project due date
            user_id: ID of user who owns this project
            
        Returns:
            Project: Newly created project instance
        """
        return cls(title, description, due_date, user_id)
    
    @classmethod
    def get_all(cls) -> List['Project']:
        """Get all projects."""
        return list(cls._all_projects.values())
    
    @classmethod
    def find_by_id(cls, project_id: int) -> Optional['Project']:
        """
        Find a project by ID.
        
        Args:
            project_id: Project ID to search for
            
        Returns:
            Optional[Project]: Found project or None
        """
        return cls._all_projects.get(project_id)
    
    @classmethod
    def find_by_user(cls, user_id: int) -> List['Project']:
        """
        Find all projects for a specific user.
        
        Args:
            user_id: User ID to find projects for
            
        Returns:
            List[Project]: List of projects belonging to user
        """
        return [project for project in cls._all_projects.values() 
                if project.user_id == user_id]
    
    @classmethod
    def find_by_title(cls, title: str) -> List['Project']:
        """
        Find projects by title (case-insensitive partial match).
        
        Args:
            title: Title to search for
            
        Returns:
            List[Project]: List of matching projects
        """
        title_lower = title.lower()
        return [project for project in cls._all_projects.values() 
                if title_lower in project.title.lower()]
    
    def add_task(self, task_id: int) -> None:
        """
        Add a task to project.
        
        Args:
            task_id: ID of task to add
        """
        if task_id not in self.tasks:
            self.tasks.append(task_id)
    
    def remove_task(self, task_id: int) -> None:
        """
        Remove a task from project.
        
        Args:
            task_id: ID of task to remove
        """
        if task_id in self.tasks:
            self.tasks.remove(task_id)
    
    def get_completion_percentage(self) -> float:
        """
        Calculate project completion percentage based on tasks.
        
        Returns:
            float: Completion percentage (0-100)
        """
        from models.task import Task
        
        if not self.tasks:
            return 0.0
        
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task_id in self.tasks 
                            if (task := Task.find_by_id(task_id)) and task.status == 'completed')
        
        return (completed_tasks / total_tasks) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project object to dictionary for JSON serialization."""
        return {
            'project_id': self.project_id,
            'title': self._title,
            'description': self._description,
            'due_date': self._due_date.isoformat(),
            'user_id': self.user_id,
            'tasks': self.tasks,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """
        Create a project object from dictionary data.
        
        Args:
            data: Dictionary containing project data
            
        Returns:
            Project: New project instance
        """
        return cls(
            title=data['title'],
            description=data['description'],
            due_date=data['due_date'],
            user_id=data['user_id'],
            project_id=data['project_id'],
            tasks=data.get('tasks', []),
            created_at=data.get('created_at')
        )
    
    @classmethod
    def load_all(cls) -> None:
        """Load all projects from JSON file."""
        data = FileHandler.load_data('projects.json')
        cls._all_projects.clear()
        cls._next_id = 1
        
        for project_data in data:
            project = cls.from_dict(project_data)
            cls._all_projects[project.project_id] = project
            if project.project_id >= cls._next_id:
                cls._next_id = project.project_id + 1
    
    @classmethod
    def save_all(cls) -> None:
        """Save all projects to JSON file."""
        data = [project.to_dict() for project in cls._all_projects.values()]
        FileHandler.save_data('projects.json', data)
    
    def __str__(self) -> str:
        """String representation for CLI output."""
        due_str = self._due_date.strftime('%Y-%m-%d')
        overdue = " (OVERDUE)" if self.is_overdue else ""
        return f"Project(ID: {self.project_id}, Title: {self.title}, Due: {due_str}{overdue}, Tasks: {len(self.tasks)})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"Project(project_id={self.project_id}, title='{self.title}', user_id={self.user_id})"