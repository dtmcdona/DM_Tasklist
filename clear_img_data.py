from pathlib import Path


def clear_img_data():
    base_dir = Path("").absolute()
    resources_dir = base_dir / "app" / "core" / "resources"
    for data in ("images", "screenshot", "screen_data"):
        data_dir = resources_dir / data
        for file_path in data_dir.iterdir():
            if file_path.name not in ("test_image.json", "test_image.png", "black_screen.json", "test_screen_data.json", "test_screen_data_object.json"):
                file_path.unlink()


clear_img_data()
