# Project Management CLI Tool

A powerful command-line interface tool for managing users, projects, and tasks in a team environment. This tool provides a comprehensive set of commands for administrators to manage project workflows efficiently.

## Features

- **User Management**: Create, list, and search users
- **Project Management**: Create projects, track due dates, monitor completion status
- **Task Management**: Create tasks, assign to users, track status, mark as complete
- **Advanced Search**: Search across all entities with a single command
- **Data Persistence**: Automatic saving/loading using JSON files
- **Rich CLI Interface**: Beautiful formatted output using the `rich` library
- **Relationships**: One-to-many (User → Projects) and many-to-many (Tasks ↔ Users) relationships
- **Validation**: Input validation for emails, dates, and required fields

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CaltonMomaya/Summative-Lab-Python-Project-Management-CLI-Tool-
cd project-management-cli