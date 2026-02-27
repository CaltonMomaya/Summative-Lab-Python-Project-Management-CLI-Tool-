from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from utils.file_handler import FileHandler

class Task:
    """
    Task class representing a task in a project.
    
    Attributes:
        task_id (int): Unique identifier for the task
        title (str): Task title
        description (str): Task description
        status (str): Task status ('pending', 'in_progress', 'completed')
        project_id (int): ID of project this task belongs to
        assigned_users (List[int]): List of user IDs assigned to this task (many-to-many)
        created_at (str): Timestamp when task was created
    """
    
    # Class attribute to track all tasks
    _all_tasks: Dict[int, 'Task'] = {}
    _next_id: int = 1
    
    # Valid statuses
    VALID_STATUSES = ['pending', 'in_progress', 'completed']
    
    def __init__(self, title: str, description: str, project_id: int,
                 task_id: Optional[int] = None, status: str = 'pending',
                 assigned_users: Optional[List[int]] = None,
                 created_at: Optional[str] = None):
        """
        Initialize a new Task instance.
        
        Args:
            title: Task title
            description: Task description
            project_id: ID of project this task belongs to
            task_id: Optional task ID (auto-generated if not provided)
            status: Task status
            assigned_users: Optional list of assigned user IDs
            created_at: Optional creation timestamp
            
        Raises:
            ValueError: If status is invalid
        """
        self.task_id = task_id or Task._get_next_id()
        self._title = title
        self._description = description
        self._status = status
        self.project_id = project_id
        self.assigned_users = assigned_users or []
        self.created_at = created_at or datetime.now().isoformat()
        
        # Validate status
        if self._status not in Task.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(Task.VALID_STATUSES)}")
        
        # Add to class registry
        Task._all_tasks[self.task_id] = self
    
    @property
    def title(self) -> str:
        """Get task title."""
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        """
        Set task title with validation.
        
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
        """Get task description."""
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        """Set task description."""
        self._description = value.strip() if value else ""
    
    @property
    def status(self) -> str:
        """Get task status."""
        return self._status
    
    @status.setter
    def status(self, value: str) -> None:
        """
        Set task status with validation.
        
        Args:
            value: New status value
            
        Raises:
            ValueError: If status is invalid
        """
        if value not in Task.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(Task.VALID_STATUSES)}")
        self._status = value
    
    def mark_complete(self) -> None:
        """Mark task as completed."""
        self.status = 'completed'
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self._status == 'completed'
    
    @classmethod
    def _get_next_id(cls) -> int:
        """Get the next available task ID."""
        current_id = cls._next_id
        cls._next_id += 1
        return current_id
    
    @classmethod
    def create(cls, title: str, description: str, project_id: int) -> 'Task':
        """
        Factory method to create a new task.
        
        Args:
            title: Task title
            description: Task description
            project_id: ID of project this task belongs to
            
        Returns:
            Task: Newly created task instance
        """
        return cls(title, description, project_id)
    
    @classmethod
    def get_all(cls) -> List['Task']:
        """Get all tasks."""
        return list(cls._all_tasks.values())
    
    @classmethod
    def find_by_id(cls, task_id: int) -> Optional['Task']:
        """
        Find a task by ID.
        
        Args:
            task_id: Task ID to search for
            
        Returns:
            Optional[Task]: Found task or None
        """
        return cls._all_tasks.get(task_id)
    
    @classmethod
    def find_by_project(cls, project_id: int) -> List['Task']:
        """
        Find all tasks for a specific project.
        
        Args:
            project_id: Project ID to find tasks for
            
        Returns:
            List[Task]: List of tasks belonging to project
        """
        return [task for task in cls._all_tasks.values() 
                if task.project_id == project_id]
    
    @classmethod
    def find_by_user(cls, user_id: int) -> List['Task']:
        """
        Find all tasks assigned to a specific user.
        
        Args:
            user_id: User ID to find tasks for
            
        Returns:
            List[Task]: List of tasks assigned to user
        """
        return [task for task in cls._all_tasks.values() 
                if user_id in task.assigned_users]
    
    @classmethod
    def find_by_status(cls, status: str) -> List['Task']:
        """
        Find all tasks with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List[Task]: List of tasks with matching status
        """
        if status not in cls.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(cls.VALID_STATUSES)}")
        return [task for task in cls._all_tasks.values() 
                if task.status == status]
    
    def assign_user(self, user_id: int) -> None:
        """
        Assign a user to this task.
        
        Args:
            user_id: ID of user to assign
        """
        if user_id not in self.assigned_users:
            self.assigned_users.append(user_id)
    
    def unassign_user(self, user_id: int) -> None:
        """
        Remove a user from this task.
        
        Args:
            user_id: ID of user to remove
        """
        if user_id in self.assigned_users:
            self.assigned_users.remove(user_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task object to dictionary for JSON serialization."""
        return {
            'task_id': self.task_id,
            'title': self._title,
            'description': self._description,
            'status': self._status,
            'project_id': self.project_id,
            'assigned_users': self.assigned_users,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task object from dictionary data.
        
        Args:
            data: Dictionary containing task data
            
        Returns:
            Task: New task instance
        """
        return cls(
            title=data['title'],
            description=data['description'],
            project_id=data['project_id'],
            task_id=data['task_id'],
            status=data.get('status', 'pending'),
            assigned_users=data.get('assigned_users', []),
            created_at=data.get('created_at')
        )
    
    @classmethod
    def load_all(cls) -> None:
        """Load all tasks from JSON file."""
        data = FileHandler.load_data('tasks.json')
        cls._all_tasks.clear()
        cls._next_id = 1
        
        for task_data in data:
            task = cls.from_dict(task_data)
            cls._all_tasks[task.task_id] = task
            if task.task_id >= cls._next_id:
                cls._next_id = task.task_id + 1
    
    @classmethod
    def save_all(cls) -> None:
        """Save all tasks to JSON file."""
        data = [task.to_dict() for task in cls._all_tasks.values()]
        FileHandler.save_data('tasks.json', data)
    
    def __str__(self) -> str:
        """String representation for CLI output."""
        status_symbol = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅'
        }.get(self._status, '❓')
        
        return f"Task(ID: {self.task_id}) {status_symbol} {self.title} [{self._status}] (Assigned: {len(self.assigned_users)})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"Task(task_id={self.task_id}, title='{self.title}', status='{self.status}')"