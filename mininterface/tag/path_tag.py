from typing import Optional
from ..auxiliary import common_iterables
from . import Tag


from dataclasses import dataclass
from pathlib import Path


@dataclass(repr=False)
class PathTag(Tag):
    """
    Contains a Path or their list. Use this helper object to select files.

    In the following example, we see that it is not always needed to use this
    object.

    * File 1 – plain detection, button to a file picker appeared.
    * File 2 – the same.
    * File 3 – we specified multiple paths can be selected.

    ```python
    from pathlib import Path
    from mininterface import run, Tag
    from mininterface.tag import PathTag

    m = run()
    out = m.form({
        "File 1": Path("/tmp"),
        "File 2": Tag("", annotation=Path),
        "File 3": PathTag([Path("/tmp")], multiple=True),
    })
    print(out)
    # {'File 1': PosixPath('/tmp'), 'File 2': PosixPath('.')}
    # {'File 3': [PosixPath('/tmp')]}
    ```

    ![File picker](asset/file_picker.avif)
    """
    multiple: Optional[bool] = None
    """ The user can select multiple files. """

    exist: Optional[bool] = None
    """ If True, validates that the selected file exists """

    is_dir: Optional[bool] = None
    """ If True, validates that the selected path is a directory """

    is_file: Optional[bool] = None
    """ If True, validates that the selected path is a file """

    def __post_init__(self):
        # Determine annotation from multiple
        if not self.annotation and self.multiple is not None:
            self.annotation = list[Path] if self.multiple else Path

        # Determine the annotation from the value and correct it,
        # as the Tag.guess_type will fetch a mere `str` from `PathTag("/var")`
        super().__post_init__()
        if self.annotation == str:  # PathTag("/var")
            self.annotation = Path
        if self.annotation == list[str]:  # PathTag(["/var"])
            self.annotation = list[Path]
        if self.annotation == list:  # PathTag([])
            self.annotation = list[Path]

        # Determine multiple from annotation
        if self.multiple is None:
            for origin, _ in self._get_possible_types():
                if origin in common_iterables:
                    self.multiple = True
                    break

    def _validate(self, value):
        """Validate the path value based on exist and is_dir attributes"""

        value = super()._validate(value)
        # Check for multiple paths before any conversion
        if not self.multiple and isinstance(value, (list, tuple)):
            self.set_error_text("Multiple paths are not allowed")
            raise ValueError()
        # Convert to list for validation
        paths = value if isinstance(value, list) else [value]

        # Validate each path
        for path in paths:
            if not isinstance(path, Path):
                try:
                    path = Path(path)
                except Exception:
                    self.set_error_text(f"Invalid path format: {path}")
                    raise ValueError()

            if self.exist and not path.exists():
                self.set_error_text(f"Path does not exist: {path}")
                raise ValueError()

            if self.is_dir and self.is_file:
                self.set_error_text(f"Path cannot be both a file and a directory: {path}")
                raise ValueError()

            if self.is_dir and not path.is_dir():
                self.set_error_text(f"Path is not a directory: {path}")
                raise ValueError()

            if self.is_file and not path.is_file():
                self.set_error_text(f"Path is not a file: {path}")
                raise ValueError()

        return value
