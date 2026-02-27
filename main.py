#!/usr/bin/env python3
"""
Project Management CLI Tool
A command-line interface for managing users, projects, and tasks.
"""

import argparse
import sys
from typing import List, Optional
from rich.console import Console
from rich import print

from models import User, Project, Task
from utils.helpers import (
    display_users_table, display_projects_table, display_tasks_table,
    print_success, print_error, print_warning, print_info,
    confirm_action, get_user_input, display_header, validate_email, validate_date
)

console = Console()

class ProjectManagementCLI:
    """
    Main CLI application class for project management.
    Handles command parsing and execution.
    """
    
    def __init__(self):
        """Initialize the CLI application."""
        self.load_data()
    
    def load_data(self):
        """Load all data from JSON files."""
        try:
            User.load_all()
            Project.load_all()
            Task.load_all()
            print_info("Data loaded successfully")
        except Exception as e:
            print_error(f"Error loading data: {e}")
    
    def save_data(self):
        """Save all data to JSON files."""
        try:
            User.save_all()
            Project.save_all()
            Task.save_all()
            print_success("Data saved successfully")
        except Exception as e:
            print_error(f"Error saving data: {e}")
    
    def run(self):
        """Main entry point for the CLI application."""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if not hasattr(args, 'func'):
            parser.print_help()
            return
        
        try:
            args.func(args)
            self.save_data()
        except Exception as e:
            print_error(f"Error: {e}")
    
    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create the argument parser with all subcommands.
        
        Returns:
            argparse.ArgumentParser: Configured parser
        """
        parser = argparse.ArgumentParser(
            description='Project Management CLI Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py add-user --name "John Doe" --email "john@example.com"
  python main.py list-users
  python main.py add-project --user "John Doe" --title "New Project" --due-date "2024-12-31"
  python main.py list-projects --user "John Doe"
  python main.py add-task --project "New Project" --title "Implement feature" --description "Add new feature"
  python main.py complete-task --task-id 1
            """
        )
        
        subparsers = parser.add_subparsers(title='commands', dest='command')
        
        # User commands
        self._add_user_commands(subparsers)
        
        # Project commands
        self._add_project_commands(subparsers)
        
        # Task commands
        self._add_task_commands(subparsers)
        
        # Search commands
        self._add_search_commands(subparsers)
        
        return parser
    
    def _add_user_commands(self, subparsers):
        """Add user-related commands."""
        # Add user
        parser_add_user = subparsers.add_parser('add-user', help='Add a new user')
        parser_add_user.add_argument('--name', required=True, help='User name')
        parser_add_user.add_argument('--email', required=True, help='User email')
        parser_add_user.set_defaults(func=self.add_user)
        
        # List users
        parser_list_users = subparsers.add_parser('list-users', help='List all users')
        parser_list_users.add_argument('--name', help='Filter by name')
        parser_list_users.set_defaults(func=self.list_users)
        
        # Show user details
        parser_show_user = subparsers.add_parser('show-user', help='Show user details')
        parser_show_user.add_argument('--user-id', type=int, help='User ID')
        parser_show_user.add_argument('--name', help='User name')
        parser_show_user.set_defaults(func=self.show_user)
    
    def _add_project_commands(self, subparsers):
        """Add project-related commands."""
        # Add project
        parser_add_project = subparsers.add_parser('add-project', help='Add a new project')
        parser_add_project.add_argument('--user', required=True, help='User name or ID')
        parser_add_project.add_argument('--title', required=True, help='Project title')
        parser_add_project.add_argument('--description', default='', help='Project description')
        parser_add_project.add_argument('--due-date', required=True, help='Due date (YYYY-MM-DD)')
        parser_add_project.set_defaults(func=self.add_project)
        
        # List projects
        parser_list_projects = subparsers.add_parser('list-projects', help='List projects')
        parser_list_projects.add_argument('--user', help='Filter by user name or ID')
        parser_list_projects.add_argument('--overdue', action='store_true', help='Show only overdue projects')
        parser_list_projects.set_defaults(func=self.list_projects)
        
        # Show project details
        parser_show_project = subparsers.add_parser('show-project', help='Show project details')
        parser_show_project.add_argument('--project-id', type=int, required=True, help='Project ID')
        parser_show_project.set_defaults(func=self.show_project)
    
    def _add_task_commands(self, subparsers):
        """Add task-related commands."""
        # Add task
        parser_add_task = subparsers.add_parser('add-task', help='Add a new task')
        parser_add_task.add_argument('--project', required=True, help='Project title or ID')
        parser_add_task.add_argument('--title', required=True, help='Task title')
        parser_add_task.add_argument('--description', default='', help='Task description')
        parser_add_task.add_argument('--assign', action='append', help='Assign to user (can be used multiple times)')
        parser_add_task.set_defaults(func=self.add_task)
        
        # List tasks
        parser_list_tasks = subparsers.add_parser('list-tasks', help='List tasks')
        parser_list_tasks.add_argument('--project', help='Filter by project title or ID')
        parser_list_tasks.add_argument('--user', help='Filter by assigned user name or ID')
        parser_list_tasks.add_argument('--status', choices=['pending', 'in_progress', 'completed'], 
                                      help='Filter by status')
        parser_list_tasks.set_defaults(func=self.list_tasks)
        
        # Update task status
        parser_update_task = subparsers.add_parser('update-task', help='Update task status')
        parser_update_task.add_argument('--task-id', type=int, required=True, help='Task ID')
        parser_update_task.add_argument('--status', required=True, 
                                       choices=['pending', 'in_progress', 'completed'],
                                       help='New status')
        parser_update_task.set_defaults(func=self.update_task)
        
        # Complete task
        parser_complete_task = subparsers.add_parser('complete-task', help='Mark task as completed')
        parser_complete_task.add_argument('--task-id', type=int, required=True, help='Task ID')
        parser_complete_task.set_defaults(func=self.complete_task)
        
        # Assign task
        parser_assign_task = subparsers.add_parser('assign-task', help='Assign task to user')
        parser_assign_task.add_argument('--task-id', type=int, required=True, help='Task ID')
        parser_assign_task.add_argument('--user', required=True, help='User name or ID')
        parser_assign_task.set_defaults(func=self.assign_task)
    
    def _add_search_commands(self, subparsers):
        """Add search commands."""
        # Search
        parser_search = subparsers.add_parser('search', help='Search across all entities')
        parser_search.add_argument('--query', required=True, help='Search query')
        parser_search.set_defaults(func=self.search)
    
    # User command implementations
    def add_user(self, args):
        """Add a new user."""
        display_header("Add New User")
        
        # Validate email
        if not validate_email(args.email):
            print_error("Invalid email format")
            return
        
        # Create user
        user = User.create(args.name, args.email)
        print_success(f"User created successfully: {user}")
    
    def list_users(self, args):
        """List users with optional filtering."""
        display_header("Users List")
        
        users = User.get_all()
        
        if args.name:
            users = User.find_by_name(args.name)
        
        display_users_table(users)
        print_info(f"Total: {len(users)} user(s)")
    
    def show_user(self, args):
        """Show detailed user information."""
        display_header("User Details")
        
        user = None
        if args.user_id:
            user = User.find_by_id(args.user_id)
        elif args.name:
            users = User.find_by_name(args.name)
            if users:
                user = users[0]
                if len(users) > 1:
                    print_warning(f"Found multiple users with name '{args.name}'. Showing first match.")
        
        if not user:
            print_error("User not found")
            return
        
        # Display user info
        console.print(f"[bold]ID:[/bold] {user.user_id}")
        console.print(f"[bold]Name:[/bold] {user.name}")
        console.print(f"[bold]Email:[/bold] {user.email}")
        console.print(f"[bold]Created:[/bold] {user.created_at}")
        console.print(f"[bold]Total Projects:[/bold] {len(user.projects)}")
        
        # Show user's projects
        if user.projects:
            print_info("Projects:")
            projects = [p for p in Project.get_all() if p.project_id in user.projects]
            display_projects_table(projects, show_tasks=True)
        
        # Show user's tasks
        tasks = Task.find_by_user(user.user_id)
        if tasks:
            print_info("Assigned Tasks:")
            display_tasks_table(tasks, show_project=True)
    
    # Project command implementations
    def add_project(self, args):
        """Add a new project."""
        display_header("Add New Project")
        
        # Find the user
        user = self._find_user(args.user)
        if not user:
            print_error(f"User '{args.user}' not found")
            return
        
        # Validate date
        if not validate_date(args.due_date):
            print_error("Invalid date format. Use YYYY-MM-DD")
            return
        
        # Create project
        project = Project.create(args.title, args.description, args.due_date, user.user_id)
        user.add_project(project.project_id)
        
        print_success(f"Project created successfully: {project}")
    
    def list_projects(self, args):
        """List projects with optional filtering."""
        display_header("Projects List")
        
        projects = Project.get_all()
        
        if args.user:
            user = self._find_user(args.user)
            if user:
                projects = [p for p in projects if p.user_id == user.user_id]
            else:
                print_warning(f"User '{args.user}' not found")
        
        if args.overdue:
            projects = [p for p in projects if p.is_overdue]
        
        display_projects_table(projects, show_tasks=True)
        print_info(f"Total: {len(projects)} project(s)")
    
    def show_project(self, args):
        """Show detailed project information."""
        display_header("Project Details")
        
        project = Project.find_by_id(args.project_id)
        if not project:
            print_error(f"Project with ID {args.project_id} not found")
            return
        
        # Display project info
        console.print(f"[bold]ID:[/bold] {project.project_id}")
        console.print(f"[bold]Title:[/bold] {project.title}")
        console.print(f"[bold]Description:[/bold] {project.description or 'No description'}")
        console.print(f"[bold]Due Date:[/bold] {project.due_date.strftime('%Y-%m-%d')}")
        console.print(f"[bold]Status:[/bold] {'⚠️ OVERDUE' if project.is_overdue else '✅ On Track'}")
        console.print(f"[bold]Completion:[/bold] {project.get_completion_percentage():.1f}%")
        
        # Show owner
        owner = User.find_by_id(project.user_id)
        if owner:
            console.print(f"[bold]Owner:[/bold] {owner.name} (ID: {owner.user_id})")
        
        # Show tasks
        if project.tasks:
            print_info("Tasks:")
            tasks = [t for t in Task.get_all() if t.task_id in project.tasks]
            display_tasks_table(tasks, show_project=False)
        else:
            print_info("No tasks in this project.")
    
    # Task command implementations
    def add_task(self, args):
        """Add a new task."""
        display_header("Add New Task")
        
        # Find the project
        project = self._find_project(args.project)
        if not project:
            print_error(f"Project '{args.project}' not found")
            return
        
        # Create task
        task = Task.create(args.title, args.description, project.project_id)
        project.add_task(task.task_id)
        
        # Assign users if specified
        if args.assign:
            for assignee in args.assign:
                user = self._find_user(assignee)
                if user:
                    task.assign_user(user.user_id)
                    print_info(f"Assigned task to {user.name}")
                else:
                    print_warning(f"User '{assignee}' not found, skipping assignment")
        
        print_success(f"Task created successfully: {task}")
    
    def list_tasks(self, args):
        """List tasks with optional filtering."""
        display_header("Tasks List")
        
        tasks = Task.get_all()
        
        if args.project:
            project = self._find_project(args.project)
            if project:
                tasks = [t for t in tasks if t.project_id == project.project_id]
            else:
                print_warning(f"Project '{args.project}' not found")
        
        if args.user:
            user = self._find_user(args.user)
            if user:
                tasks = [t for t in tasks if user.user_id in t.assigned_users]
            else:
                print_warning(f"User '{args.user}' not found")
        
        if args.status:
            tasks = [t for t in tasks if t.status == args.status]
        
        display_tasks_table(tasks, show_project=True)
        print_info(f"Total: {len(tasks)} task(s)")
    
    def update_task(self, args):
        """Update task status."""
        display_header("Update Task")
        
        task = Task.find_by_id(args.task_id)
        if not task:
            print_error(f"Task with ID {args.task_id} not found")
            return
        
        old_status = task.status
        task.status = args.status
        
        print_success(f"Task status updated: {old_status} → {args.status}")
    
    def complete_task(self, args):
        """Mark task as completed."""
        display_header("Complete Task")
        
        task = Task.find_by_id(args.task_id)
        if not task:
            print_error(f"Task with ID {args.task_id} not found")
            return
        
        if task.is_completed:
            print_warning("Task is already completed")
            if not confirm_action("Mark as pending instead?"):
                return
            task.status = 'pending'
            print_success("Task marked as pending")
        else:
            task.mark_complete()
            print_success("Task marked as completed")
    
    def assign_task(self, args):
        """Assign task to user."""
        display_header("Assign Task")
        
        task = Task.find_by_id(args.task_id)
        if not task:
            print_error(f"Task with ID {args.task_id} not found")
            return
        
        user = self._find_user(args.user)
        if not user:
            print_error(f"User '{args.user}' not found")
            return
        
        if user.user_id in task.assigned_users:
            print_warning(f"Task already assigned to {user.name}")
            if confirm_action("Remove assignment?"):
                task.unassign_user(user.user_id)
                print_success(f"Task unassigned from {user.name}")
        else:
            task.assign_user(user.user_id)
            print_success(f"Task assigned to {user.name}")
    
    # Search command
    def search(self, args):
        """Search across all entities."""
        display_header(f"Search Results for '{args.query}'")
        
        query = args.query.lower()
        found_any = False
        
        # Search users
        users = [u for u in User.get_all() 
                if query in u.name.lower() or query in u.email.lower()]
        if users:
            print_info(f"Users ({len(users)}):")
            display_users_table(users[:5])  # Show first 5
            if len(users) > 5:
                print_info(f"... and {len(users) - 5} more")
            found_any = True
        
        # Search projects
        projects = [p for p in Project.get_all() 
                   if query in p.title.lower() or query in p.description.lower()]
        if projects:
            print_info(f"Projects ({len(projects)}):")
            display_projects_table(projects[:5])  # Show first 5
            if len(projects) > 5:
                print_info(f"... and {len(projects) - 5} more")
            found_any = True
        
        # Search tasks
        tasks = [t for t in Task.get_all() 
                if query in t.title.lower() or query in t.description.lower()]
        if tasks:
            print_info(f"Tasks ({len(tasks)}):")
            display_tasks_table(tasks[:5], show_project=True)  # Show first 5
            if len(tasks) > 5:
                print_info(f"... and {len(tasks) - 5} more")
            found_any = True
        
        if not found_any:
            print_warning("No results found")
    
    # Helper methods
    def _find_user(self, identifier: str):
        """
        Find a user by ID or name.
        
        Args:
            identifier: User ID (int) or name (str)
            
        Returns:
            Optional[User]: Found user or None
        """
        # Try as ID first
        try:
            user_id = int(identifier)
            user = User.find_by_id(user_id)
            if user:
                return user
        except ValueError:
            pass
        
        # Try as name
        users = User.find_by_name(identifier)
        if users:
            if len(users) > 1:
                print_warning(f"Multiple users found with name '{identifier}'. Using first match.")
            return users[0]
        
        return None
    
    def _find_project(self, identifier: str):
        """
        Find a project by ID or title.
        
        Args:
            identifier: Project ID (int) or title (str)
            
        Returns:
            Optional[Project]: Found project or None
        """
        # Try as ID first
        try:
            project_id = int(identifier)
            project = Project.find_by_id(project_id)
            if project:
                return project
        except ValueError:
            pass
        
        # Try as title
        projects = Project.find_by_title(identifier)
        if projects:
            if len(projects) > 1:
                print_warning(f"Multiple projects found with title '{identifier}'. Using first match.")
            return projects[0]
        
        return None

def main():
    """Main entry point."""
    try:
        cli = ProjectManagementCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n")
        print_info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()