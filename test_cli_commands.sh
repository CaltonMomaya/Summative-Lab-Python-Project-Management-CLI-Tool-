#!/bin/bash

echo "🚀 Testing Project Management CLI"
echo "================================"

# Test adding users
echo -e "\n📝 Testing: Add users"
python main.py add-user --name "Test User 1" --email "test1@example.com"
python main.py add-user --name "Test User 2" --email "test2@example.com"

# Test listing users
echo -e "\n📋 Testing: List users"
python main.py list-users

# Test adding projects
echo -e "\n📝 Testing: Add projects"
python main.py add-project --user "Test User 1" --title "Test Project 1" --due-date "2025-12-31" --description "First test project"
python main.py add-project --user "Test User 2" --title "Test Project 2" --due-date "2025-12-31" --description "Second test project"

# Test listing projects
echo -e "\n📋 Testing: List all projects"
python main.py list-projects

# Test adding tasks
echo -e "\n📝 Testing: Add tasks"
python main.py add-task --project "Test Project 1" --title "Task 1" --description "First task" --assign "Test User 1"
python main.py add-task --project "Test Project 1" --title "Task 2" --description "Second task" --assign "Test User 2"

# Test listing tasks
echo -e "\n📋 Testing: List all tasks"
python main.py list-tasks

# Test updating tasks
echo -e "\n🔄 Testing: Update task status"
python main.py update-task --task-id 1 --status in_progress
python main.py complete-task --task-id 2

echo -e "\n✅ All tests completed!"
