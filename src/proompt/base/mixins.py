class RenderStrMixin:
    """Mixin that makes ``str(obj)`` delegate to ``obj.render()``.

    The consuming class is responsible for defining ``render() -> str``.
    """

    def __str__(self) -> str:
        """String representation via ``render()``."""
        return self.render()
