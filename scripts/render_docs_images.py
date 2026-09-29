import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)
tile = ROOT / "output" / "tile_1.png"
if tile.exists():
    shutil.copy(tile, OUT / "sample_tile.png")
    print("Copied sample_tile.png")
