# Project Roadmap

## Todo List

- [ ] **Dockerfile for Python Environment**
  - Create a Dockerfile to containerize the application.
  - Ensure all dependencies (python, requirements.txt) are included.

- [ ] **Collect User Information in Daily GPU Log**
  - Enhance the daily logging script to capture user details (who is running the process).
  - Integrate with `ps` or similar tools to map PID to user.

- [ ] **Add Database**
  - Migrate from CSV/Text files to a proper database (e.g., SQLite, PostgreSQL).
  - Design schema for GPU usage, Users, and Nodes.
