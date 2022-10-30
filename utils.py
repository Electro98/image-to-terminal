from enum import Enum, EnumMeta


class _StringEnumMeta(EnumMeta):
    def __contains__(cls, obj: str) -> bool:
        if not isinstance(obj, (str, cls)):
            raise TypeError(
                f"inappropriate type of keyword value, found {type(obj)}.",
            )
        return any((
            obj in cls._value2member_map_,
            obj in cls._value2member_map_.values(),
        ))

    def __getitem__(cls, value: str) -> Enum:
        return cls._value2member_map_[value]


class StringEnum(Enum, metaclass=_StringEnumMeta):
    """Enum class with string equavalent for an each member.

    Can be checked for containing such string in members.
    """
