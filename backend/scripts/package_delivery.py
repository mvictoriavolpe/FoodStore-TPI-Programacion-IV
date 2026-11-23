"""Build a source-only ZIP with the required FoodStore/ root directory."""

from pathlib import Path
import os
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "FoodStore_Entrega.zip"
EXCLUDED_DIRS = {
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".qa",
    ".git",
    ".codex",
    ".agents",
    ".aws",
    ".pnpm-store",
    ".ruff_cache",
    "dist",
    "coverage",
    ".mypy_cache",
    ".vite",
    "test-results",
    "playwright-report",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".tsbuildinfo",
    ".zip",
    ".mp4",
    ".mov",
    ".webm",
    ".avi",
}


def include_file(path):
    return (
        path.suffix.lower() not in EXCLUDED_SUFFIXES
        and (not path.name.startswith(".env") or path.name == ".env.example")
        and path.name not in {".DS_Store", "Thumbs.db", ".coverage"}
    )


def package():
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT / "README.md", "FoodStore/README.md")
        archive.write(ROOT / ".gitignore", "FoodStore/.gitignore")
        for folder in ["backend", "frontend"]:
            for directory, subdirs, filenames in os.walk(ROOT / folder):
                subdirs[:] = sorted(
                    name for name in subdirs if name not in EXCLUDED_DIRS
                )
                for name in sorted(filenames):
                    path = Path(directory) / name
                    if include_file(path):
                        archive.write(
                            path, f"FoodStore/{path.relative_to(ROOT).as_posix()}"
                        )
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            path = Path(name)
            assert not any(part in EXCLUDED_DIRS for part in path.parts)
            assert include_file(path)
        print(
            f"{OUTPUT.name}: {len(archive.namelist())} archivos, {OUTPUT.stat().st_size:,} bytes. Sin entornos, secretos, bases de datos ni video."
        )


if __name__ == "__main__":
    package()
