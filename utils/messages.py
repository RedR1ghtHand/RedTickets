from settings import MESSAGES


def get_message(path: str, return_raw: bool = False, **kwargs):
    node = MESSAGES
    for key in path.split('.'):
        node = node.get(key)
        if node is None:
            return f"[missing message: {path}]"

    if return_raw:
        return node

    if isinstance(node, str):
        return node.format(**kwargs)
        
    return node
    