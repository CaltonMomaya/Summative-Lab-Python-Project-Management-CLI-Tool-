import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from utils.file_handler import FileHandler

class User:
    """
    User class representing a system user.
    
    Attributes:
        user_id (int): Unique identifier for the user
        name (str): User's full name
        email (str): User's email address
        created_at (str): Timestamp when user was created
        projects (List[int]): List of project IDs belonging to user
    """
    
    # Class attribute to track all users
    _all_users: Dict[int, 'User'] = {}
    _next_id: int = 1
    
    def __init__(self, name: str, email: str, user_id: Optional[int] = None, 
                 created_at: Optional[str] = None, projects: Optional[List[int]] = None):
        """
        Initialize a new User instance.
        
        Args:
            name: User's full name
            email: User's email address
            user_id: Optional user ID (auto-generated if not provided)
            created_at: Optional creation timestamp
            projects: Optional list of project IDs
        """
        self.user_id = user_id or User._get_next_id()
        self._name = name
        self._email = email
        self.created_at = created_at or datetime.now().isoformat()
        self.projects = projects or []
        
        # Add to class registry
        User._all_users[self.user_id] = self
    
    @property
    def name(self) -> str:
        """Get user's name."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """
        Set user's name with validation.
        
        Args:
            value: New name value
            
        Raises:
            ValueError: If name is empty or too short
        """
        if not value or len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        self._name = value.strip()
    
    @property
    def email(self) -> str:
        """Get user's email."""
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        """
        Set user's email with basic validation.
        
        Args:
            value: New email value
            
        Raises:
            ValueError: If email format is invalid
        """
        if '@' not in value or '.' not in value:
            raise ValueError("Invalid email format")
        self._email = value.strip()
    
    @classmethod
    def _get_next_id(cls) -> int:
        """Get the next available user ID."""
        current_id = cls._next_id
        cls._next_id += 1
        return current_id
    
    @classmethod
    def create(cls, name: str, email: str) -> 'User':
        """
        Factory method to create a new user.
        
        Args:
            name: User's name
            email: User's email
            
        Returns:
            User: Newly created user instance
        """
        return cls(name, email)
    
    @classmethod
    def get_all(cls) -> List['User']:
        """Get all users."""
        return list(cls._all_users.values())
    
    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['User']:
        """
        Find a user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            Optional[User]: Found user or None
        """
        return cls._all_users.get(user_id)
    
    @classmethod
    def find_by_name(cls, name: str) -> List['User']:
        """
        Find users by name (case-insensitive partial match).
        
        Args:
            name: Name to search for
            
        Returns:
            List[User]: List of matching users
        """
        name_lower = name.lower()
        return [user for user in cls._all_users.values() 
                if name_lower in user.name.lower()]
    
    def add_project(self, project_id: int) -> None:
        """
        Add a project to user's projects.
        
        Args:
            project_id: ID of project to add
        """
        if project_id not in self.projects:
            self.projects.append(project_id)
    
    def remove_project(self, project_id: int) -> None:
        """
        Remove a project from user's projects.
        
        Args:
            project_id: ID of project to remove
        """
        if project_id in self.projects:
            self.projects.remove(project_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for JSON serialization."""
        return {
            'user_id': self.user_id,
            'name': self._name,
            'email': self._email,
            'created_at': self.created_at,
            'projects': self.projects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a user object from dictionary data.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            User: New user instance
        """
        return cls(
            name=data['name'],
            email=data['email'],
            user_id=data['user_id'],
            created_at=data.get('created_at'),
            projects=data.get('projects', [])
        )
    
    @classmethod
    def load_all(cls) -> None:
        """Load all users from JSON file."""
        data = FileHandler.load_data('users.json')
        cls._all_users.clear()
        cls._next_id = 1
        
        for user_data in data:
            user = cls.from_dict(user_data)
            cls._all_users[user.user_id] = user
            if user.user_id >= cls._next_id:
                cls._next_id = user.user_id + 1
    
    @classmethod
    def save_all(cls) -> None:
        """Save all users to JSON file."""
        data = [user.to_dict() for user in cls._all_users.values()]
        FileHandler.save_data('users.json', data)
    
    def __str__(self) -> str:
        """String representation for CLI output."""
        return f"User(ID: {self.user_id}, Name: {self.name}, Email: {self.email}, Projects: {len(self.projects)})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"User(user_id={self.user_id}, name='{self.name}', email='{self.email}')"