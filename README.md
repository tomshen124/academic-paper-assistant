# Academic Paper Assistant Platform

A platform based on Large Language Models (LLMs) and multi-agent collaboration to assist users in academic paper topic selection, outline generation, draft writing, and reference management.

## Project Overview

The Academic Paper Assistant Platform is a comprehensive tool designed to simplify and enhance the academic writing process. The platform leverages advanced large language models and multi-agent collaboration technology to provide full-process support from topic selection to final draft.

### Core Features

- **Topic Recommendation & Analysis**: Recommend research topics based on user interests and academic fields, analyze feasibility
- **Outline Generation**: Automatically generate paper outlines, support structure customization for different types of papers
- **Paper Draft Generation**: Generate content for each section based on the outline, ensure academic style
- **Reference Management**: Automatically generate citations in standard formats, support multiple citation standards
- **Academic Search**: Search for academic literature related to research topics, support multiple search sources and parameter configurations, with high stability and error recovery capabilities
- **User Authentication**: Support user registration, login, and permission management
- **Data Persistence**: Store user data in a database to ensure data security and reliability
- **Token Management**: Track and manage users' token usage

## Quick Start

### Requirements

- Python 3.10+
- Node.js 16+
- npm 8+
- PostgreSQL 12+

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/edu-kg.git
cd edu-kg
```

2. Set up the environment

```bash
# Create and activate virtual environment
python3.10 -m venv eduvenv
source eduvenv/bin/activate  # Linux/macOS
# or
.\eduvenv\Scripts\activate  # Windows

# Install dependencies
python3.10 start.py --install-deps

# Configure environment variables
cp config/.env.example config/.env
# Edit the .env file, fill in necessary API keys and database configuration

# Create database
psql -U postgres -c "CREATE DATABASE academic_paper_assistant;"
```

3. Start the service

```bash
# Use the unified startup script
python3.10 start.py
```

Visit http://localhost:3000 to start using the platform.

## Documentation

For detailed documentation, please refer to the `docs` directory:

- [User Guide](docs/user_guide.md): Installation, configuration, and usage guide
- [Implementation Status](docs/implementation_status.md): Current feature implementation status
- [Database Design](docs/database_design.md): Database models and relationship design
- [Architecture Design](docs/architecture.md): Technical architecture documentation

Latest update documentation:

- [Academic Search Improvements](docs/updates/academic_search_improvements.md): Stability and error handling improvements for academic search functionality
- [Admin Password Reset Guide](docs/admin_password_reset.md): Usage guide for the admin password reset tool

## Technology Stack

### Backend

- FastAPI: High-performance API framework
- SQLAlchemy: Powerful ORM framework
- PostgreSQL: Relational database
- Alembic: Database migration tool
- LiteLLM: Unified LLM interface
- Loguru: Advanced logging system
- Pydantic: Data validation and settings management
- JWT: User authentication and authorization

### Frontend

- Vue.js: Progressive JavaScript framework
- Vue Router: Frontend routing management
- Pinia: State management library
- Element Plus: UI component library
- Axios: HTTP client

## Features

- **Multi-model Support**: Support for multiple LLM models including OpenAI, Anthropic, DeepSeek, etc.
- **Multi-agent Collaboration**: Multi-agent collaboration system based on the CAMEL framework
- **Configurable Academic Search**: Support for multiple academic search sources and parameter configurations, with high stability and error recovery capabilities
- **Database Persistence**: Use PostgreSQL database to store user data and application state
- **User Authentication System**: Secure user authentication and authorization based on JWT
- **Token Usage Tracking**: Detailed recording and statistics of user token usage
- **MCP Integration**: Reserved Model Context Protocol integration interface
- **Unified Startup Script**: Simplify development and deployment process
- **Advanced Logging System**: Support for log categorization, automatic splitting, compression, and retention policies
- **Intelligent Caching Mechanism**: Optimized caching service, support for caching API request results to reduce repeated requests
- **Robust Error Handling**: Comprehensive error handling and logging to improve system stability

## Database Architecture

This project uses PostgreSQL database for data persistence storage. The main data models include:

- **User Model**: Store user information and authentication data
- **Topic Model**: Store paper topic information and analysis results
- **Outline Model**: Store paper outline structure
- **Paper Model**: Store paper content
- **Citation Model**: Store paper citation information
- **TokenUsage Model**: Record user token usage

For detailed database design, please refer to the [Database Design Document](docs/database_design.md).

## Contribution

Contributions of code, issue reports, or new feature suggestions are welcome. Please refer to the [Contribution Guide](CONTRIBUTING.md) for more information.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

Thanks to all developers and researchers who have contributed to this project.
