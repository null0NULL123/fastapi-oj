__all__ = ["check_id"]
def check_id(id: str):
    return len(id) == 10 and id.startswith(prefix) and id.isnumeric()