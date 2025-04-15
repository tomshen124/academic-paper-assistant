from setuptools import setup, find_packages

setup(
    name="edu-kg",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.23",
        "alembic>=1.12.1",
        "psycopg2-binary>=2.9.9",
        "pydantic>=2.5.2",
        "pydantic-settings>=2.1.0",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.6",
        "pyyaml>=6.0.1",
    ],
) 