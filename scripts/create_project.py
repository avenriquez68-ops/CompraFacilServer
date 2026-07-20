from pathlib import Path

PROJECT_STRUCTURE = [
    "app",
    "app/api",
    "app/api/v1",
    "app/core",
    "app/domain",
    "app/infrastructure",
    "app/models",
    "app/repositories",
    "app/schemas",
    "app/services",
    "tests",
    "docs",
]

BASE_FILES = [
    "README.md",
    ".gitignore",
    ".env.example",
    "requirements.txt",
    "pyproject.toml",
]


def create_structure():

    root = Path.cwd()

    print("📁 Creando estructura del proyecto...")

    for folder in PROJECT_STRUCTURE:

        path = root / folder

        path.mkdir(parents=True, exist_ok=True)

        print(f"✔ {folder}")

    for file in BASE_FILES:

        path = root / file

        path.touch(exist_ok=True)

        print(f"✔ {file}")

    print("\nProyecto creado correctamente.")


if __name__ == "__main__":

    create_structure()