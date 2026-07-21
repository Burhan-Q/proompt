class RenderStrMixin:
    """Mixin that makes str(obj) delegate to obj.render().

    The consuming class is responsible for defining render() -> str.
    """

    def __str__(self) -> str:
        """Return the string representation via render()."""
        return self.render()
