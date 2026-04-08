import os

project_name = "house-price-mlops"

folders = [
    f"{project_name}/.github/workflows",
    f"{project_name}/notebooks",
    f"{project_name}/src/components",
    f"{project_name}/src/pipelines",
    f"{project_name}/src/config",
    f"{project_name}/src/entity",
    f"{project_name}/src/exception",
    f"{project_name}/src/logger",
    f"{project_name}/src/utils",
    f"{project_name}/src/constants",
    f"{project_name}/app",
]

files = [
    f"{project_name}/src/config/configuration.py",
    f"{project_name}/Dockerfile",
    f"{project_name}/requirements.txt",
    f"{project_name}/setup.py",
    f"{project_name}/README.md",
]

def create_structure():
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    for file in files:
        with open(file, "w") as f:
            pass
        print(f"Created file: {file}")

if __name__ == "__main__":
    create_structure()