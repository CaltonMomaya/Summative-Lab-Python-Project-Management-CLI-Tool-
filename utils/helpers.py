from typing import List, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint
import logging

console = Console()

def setup_logging(level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def print_success(message: str) -> None:
    """
    Print a success message in green.
    
    Args:
        message: Message to print
    """
    console.print(f"✅ {message}", style="bold green")

def print_error(message: str) -> None:
    """
    Print an error message in red.
    
    Args:
        message: Message to print
    """
    console.print(f"❌ {message}", style="bold red")

def print_warning(message: str) -> None:
    """
    Print a warning message in yellow.
    
    Args:
        message: Message to print
    """
    console.print(f"⚠️  {message}", style="bold yellow")

def print_info(message: str) -> None:
    """
    Print an info message in blue.
    
    Args:
        message: Message to print
    """
    console.print(f"ℹ️  {message}", style="bold blue")

def display_users_table(users: List[Any]) -> None:
    """
    Display users in a formatted table.
    
    Args:
        users: List of User objects
    """
    if not users:
        print_warning("No users found.")
        return
    
    table = Table(title="Users", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name", width=20)
    table.add_column("Email", width=25)
    table.add_column("Projects", justify="center", width=10)
    table.add_column("Created", width=20)
    
    for user in users:
        created = datetime.fromisoformat(user.created_at).strftime('%Y-%m-%d %H:%M')
        table.add_row(
            str(user.user_id),
            user.name,
            user.email,
            str(len(user.projects)),
            created
        )
    
    console.print(table)

def display_projects_table(projects: List[Any], show_tasks: bool = False) -> None:
    """
    Display projects in a formatted table.
    
    Args:
        projects: List of Project objects
        show_tasks: Whether to show task counts
    """
    if not projects:
        print_warning("No projects found.")
        return
    
    table = Table(title="Projects", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", width=30)
    table.add_column("Due Date", width=12)
    table.add_column("Status", width=10)
    table.add_column("Progress", width=10)
    
    if show_tasks:
        table.add_column("Tasks", justify="center", width=8)
    
    table.add_column("User ID", justify="center", width=8)
    
    for project in projects:
        due_date = project.due_date.strftime('%Y-%m-%d')
        status = "⚠️ OVERDUE" if project.is_overdue else "✅ On Track"
        progress = f"{project.get_completion_percentage():.1f}%"
        
        row = [
            str(project.project_id),
            project.title[:27] + "..." if len(project.title) > 30 else project.title,
            due_date,
            status,
            progress,
        ]
        
        if show_tasks:
            row.append(str(len(project.tasks)))
        
        row.append(str(project.user_id))
        table.add_row(*row)
    
    console.print(table)

def display_tasks_table(tasks: List[Any], show_project: bool = False) -> None:
    """
    Display tasks in a formatted table.
    
    Args:
        tasks: List of Task objects
        show_project: Whether to show project ID
    """
    if not tasks:
        print_warning("No tasks found.")
        return
    
    table = Table(title="Tasks", show_header=True, header_style="bold green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", width=30)
    table.add_column("Status", width=12)
    table.add_column("Assigned Users", justify="center", width=12)
    
    if show_project:
        table.add_column("Project ID", justify="center", width=10)
    
    status_colors = {
        'pending': 'yellow',
        'in_progress': 'blue',
        'completed': 'green'
    }
    
    for task in tasks:
        status_style = status_colors.get(task.status, 'white')
        assigned_count = len(task.assigned_users)
        
        row = [
            str(task.task_id),
            task.title[:27] + "..." if len(task.title) > 30 else task.title,
            f"[{status_style}]{task.status}[/{status_style}]",
            str(assigned_count)
        ]
        
        if show_project:
            row.append(str(task.project_id))
        
        table.add_row(*row)
    
    console.print(table)

def confirm_action(message: str) -> bool:
    """
    Ask user to confirm an action.
    
    Args:
        message: Confirmation message
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    return Confirm.ask(message, default=False)

def get_user_input(prompt: str, required: bool = True) -> Optional[str]:
    """
    Get user input with optional validation.
    
    Args:
        prompt: Input prompt
        required: Whether input is required
        
    Returns:
        Optional[str]: User input or None if cancelled
    """
    while True:
        value = Prompt.ask(prompt)
        if value or not required:
            return value
        print_error("This field is required.")

def display_header(title: str) -> None:
    """
    Display a formatted header.
    
    Args:
        title: Header title
    """
    console.print(Panel.fit(title, style="bold blue"))

def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email to validate
        
    Returns:
        bool: True if valid
    """
    return '@' in email and '.' in email and len(email) >= 5

def validate_date(date_str: str) -> bool:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if valid
    """
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False