from datetime import datetime
import os

from app.core.config import settings


def generate_time() -> str:
    date = datetime.utcnow()
    return date.strftime("%Y%m")


def generate_path() -> str:
    storage_path = settings.file_storage_path + '/' + generate_time() + '/'
    full_path = os.path.join(os.getcwd(), storage_path)
    return full_path


def generate_filename(filename: str) -> str:
    date = datetime.utcnow()
    name = filename.lower().split(".")
    name_l = len(name)
    name_suffix = name[-1]
    if name_l > 2:
        name = '.'.join(name[:-1])
    else:
        name = name[0]

    name = name + '_' + date.strftime("%d%H%M%S") + '.' + name_suffix
    return name
