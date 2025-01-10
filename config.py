import pandas as pd
__all__ = [
    "UPLOAD_DIR",
    "DOWNLOAD_DIR",
    "ids",
    "data",
    "roles",
    "prefix",
    "size",
]
UPLOAD_DIR = "uploads"
DOWNLOAD_DIR = "downloads"
roles = ["Python", "C", "MCU"]
data = pd.read_csv("data.csv")
ids = set(data["id"].astype(str))
prefix = "2"
size = 10
