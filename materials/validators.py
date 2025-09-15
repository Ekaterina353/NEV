from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_video_url(value):
    """
    Валидатор для проверки ссылок на видео.
    Разрешает только ссылки на youtube.com
    """
    if not value:
        return

    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower()

    # Разрешаем только youtube.com и его поддомены
    if not (
        domain == "youtube.com"
        or domain == "www.youtube.com"
        or domain.endswith(".youtube.com")
    ):
        raise ValidationError(
            "Разрешены только ссылки на YouTube. Ссылки на сторонние образовательные платформы или личные сайты запрещены."
        )


class VideoURLValidator:
    """
    Класс-валидатор для проверки ссылок на видео
    """

    def __init__(self, field="video_url"):
        self.field = field

    def __call__(self, attrs):
        video_url = attrs.get(self.field)
        if video_url:
            validate_video_url(video_url)
        return attrs
