from pathlib import Path


def clear_all_collections():
    base_dir = Path("").absolute()
    resources_dir = base_dir / "app" / "core" / "resources"
    for collection in ("actions", "tasks", "schedules"):
        collection_dir = resources_dir / collection
        for file_path in collection_dir.iterdir():
            file_path.unlink()


clear_all_collections()