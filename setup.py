from setuptools import setup, find_packages

setup(
    name="aquamarine",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "aquamarine": ["../alembic.ini"],
    },
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "python-dotenv",
        "alembic",
    ],
    python_requires=">=3.8",
) 
