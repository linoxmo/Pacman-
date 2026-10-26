from pydantic import BaseModel, Field, ValidationError, ValidationInfo
from pydantic import ValidatorFunctionWrapHandler
from pydantic import field_validator, model_validator
from typing import Any
import json


class SafeModel(BaseModel):
    """Base model that fixes the wrong values instead of crashing.
    Args: none.
    Returns: none."""

    @model_validator(mode="before")
    @classmethod
    def check_keys(cls, data: Any) -> Any:
        """Print a message for each missing or unknown key.
        Args: data is the content of the config file.
        Returns: the data unchanged."""

        if not isinstance(data, dict):
            return data
        for key in cls.model_fields:
            if key not in data:
                print(f"Warning: '{key}' is missing, default value is used")
        for key in data:
            if key not in cls.model_fields:
                print(f"Warning: unknown key '{key}' is ignored")
        return data

    @field_validator("*", mode="wrap")
    @classmethod
    def clamp_value(cls, value: Any, handler: ValidatorFunctionWrapHandler,
                    info: ValidationInfo) -> Any:
        """Check one value: if it is too small or too big, use the limit.
        If it is wrong, use the default value.
        Args: value is the value to check, handler is the pydantic check
        and info gives the name of the key.
        Returns: the checked value."""

        name: str = str(info.field_name)
        try:
            return handler(value)
        except ValidationError as e:
            error = e.errors()[0]
            limits: dict[str, Any] = error.get("ctx", {})
            if error["type"] == "greater_than_equal":
                print(f"Warning: '{name}' = {value!r} is too small, "
                      f"clamped to {limits['ge']}")
                return limits["ge"]
            if error["type"] == "less_than_equal":
                print(f"Warning: '{name}' = {value!r} is too big, "
                      f"clamped to {limits['le']}")
                return limits["le"]
            print(f"Warning: '{name}' = {value!r} is invalid, "
                  "default value is used")
            return cls.model_fields[name].get_default(
                call_default_factory=True)


class Level(SafeModel):
    """Size of the maze of one level.
    Args: width and height in cells.
    Returns: none."""

    width: int = Field(default=15, ge=11, le=50, strict=True)
    height: int = Field(default=11, ge=11, le=50, strict=True)


def default_levels() -> list[Level]:
    """Create the 10 default levels.
    Args: none.
    Returns: the list of levels."""

    sizes: list[tuple[int, int]] = [(15, 11), (15, 13), (17, 13), (17, 15),
                                    (19, 15), (19, 17), (21, 17), (21, 19),
                                    (23, 19), (25, 21)]
    return [Level(width=w, height=h) for w, h in sizes]


class Config(SafeModel):
    """Game configuration with its default values and limits.
    Args: the keys of the config file.
    Returns: none."""

    highscore_filename: str = Field(default="highscores.json",
                                    min_length=1, strict=True)
    lives: int = Field(default=3, ge=1, le=99, strict=True)
    player_speed: float = Field(default=6.0, ge=1, le=20, strict=True)
    points_per_pacgum: int = Field(default=10, ge=0, le=10000, strict=True)
    points_per_super_pacgum: int = Field(default=50, ge=0, le=10000,
                                         strict=True)
    points_per_ghost: int = Field(default=200, ge=0, le=10000, strict=True)
    ghost_speed: float = Field(default=5.0, ge=1, le=20, strict=True)
    edible_time: float = Field(default=7.0, ge=1, le=60, strict=True)
    ghost_respawn_time: float = Field(default=5.0, ge=0, le=60, strict=True)
    seed: int = Field(default=42, ge=0, strict=True)
    level_max_time: int = Field(default=90, ge=10, le=999, strict=True)
    levels: list[Level] = Field(default_factory=default_levels, min_length=1)


def read_file(path: str) -> dict[str, Any] | None:
    """Read the config file without the # lines.
    Args: path is the config file.
    Returns: the content as a dict, or None if there is an error."""

    try:
        with open(path, "r", encoding="utf-8") as file:
            lines: list[str] = [
                "\n" if line.lstrip().startswith("#") else line
                for line in file]
        data: Any = json.loads("".join(lines))
    except OSError as e:
        print(f"Error: can't read '{path}' ({e.strerror})")
        return None
    except UnicodeDecodeError:
        print(f"Error: '{path}' is not a text file")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: '{path}' is not a valid json file "
              f"(line {e.lineno}: {e.msg})")
        return None
    if not isinstance(data, dict):
        print(f"Error: '{path}' must contain a json object {{...}}")
        return None
    return data


def create_conf(path: str) -> Config:
    """Create the game configuration from the config file.
    Args: path is the config file.
    Returns: the configuration, or the default one if there is an error."""

    data: dict[str, Any] | None = read_file(path)
    if data is None:
        print("Default config is used")
        return Config.model_construct()
    try:
        return Config.model_validate(data)
    except ValidationError:
        print("Error: invalid config, default config is used")
        return Config.model_construct()
