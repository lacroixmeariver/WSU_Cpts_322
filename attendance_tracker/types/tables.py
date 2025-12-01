"""Define tuple types representing sqlite tables."""

from typing import ClassVar, NamedTuple, Self


class Table(NamedTuple):
    """Abstract table class for sqlite tables."""

    TABLE_NAME = ClassVar[str]


class ClubData(NamedTuple):
    """Club data table instance."""

    TABLE_NAME = "CLUB_DATA"

    club_name: str
    club_president: str
    email: str
    club_size: int
    club_advisor: str
    club_advisor_email: str

    @property
    def insert_format(self) -> str:
        """Create insert string to be used with sqlite db."""
        cols = ", ".join(self._fields)
        return f"INSERT INTO {self.TABLE_NAME} ({cols}) VALUES (?,?,?,?,?,?)"

    @classmethod
    def from_list(cls, csv_line: list[str]) -> Self:
        """Create ClubData instance from raw list of str input."""
        match csv_line:
            case [n, p, e, s, a, a_e]:
                return cls(
                    n,
                    p,
                    e,
                    int(s),
                    a,
                    a_e,
                )
            case _:
                msg = f"unrecognized input str {csv_line}"
                raise ValueError(msg)


class InputData(NamedTuple):
    """Raw CSV input data straight from the source."""

    TABLE_NAME = "INPUT_DATA"

    building: str
    room_num: str
    times_accessed: int
    access_succeed: int
    access_fail: int
    date_entered: str

    @property
    def insert_format(self) -> str:
        """Create insert string to be used with sqlite db."""
        cols = ", ".join(self._fields)
        return f"INSERT INTO {self.TABLE_NAME} ({cols}) VALUES (?,?,?,?,?,?)"

    @classmethod
    def from_list(cls, csv_line: list[str]) -> Self:
        """Create InputData instance from raw list of str input."""
        match csv_line:
            case [b, r, t, s, f, d]:
                return cls(
                    b,
                    r,
                    int(t),
                    int(s),
                    int(f),
                    d,
                )
            case _:
                msg = f"unrecognized input str {csv_line}"
                raise ValueError(msg)


class RoomLog(NamedTuple):
    """Room to club relation table."""

    TABLE_NAME = "ROOM_LOG"

    building: str
    room_num: int
    assigned_club: str

    @property
    def insert_format(self) -> str:
        """Create insert string to be used with sqlite db."""
        cols = ", ".join(self._fields)
        return f"INSERT INTO {self.TABLE_NAME} ({cols}) VALUES (?,?,?)"

    @classmethod
    def from_list(cls, csv_line: list[str]) -> Self:
        """Create RoomLog instance from raw list of str input."""
        match csv_line:
            case [b, r, c]:
                return cls(
                    b,
                    int(r),
                    c,
                )
            case _:
                msg = f"unrecognized input str {csv_line}"
                raise ValueError(msg)
