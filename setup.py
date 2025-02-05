from setuptools import setup, find_packages

setup(
    name="vivita-inventory",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "supabase",
        "python-dotenv",
        "plotly",
        "pytest"
    ]
)
