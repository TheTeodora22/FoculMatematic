AVATAR_IMAGES = {
    "default_avatar": "core/img/avatars/default.svg",
    "dragon_avatar": "core/img/avatars/dragon.svg",
    "phoenix_avatar": "core/img/avatars/phoenix.svg",
}

DEFAULT_AVATAR_KEY = "default_avatar"


def get_avatar_static_path(key: str) -> str:
    return AVATAR_IMAGES.get(key, AVATAR_IMAGES[DEFAULT_AVATAR_KEY])
