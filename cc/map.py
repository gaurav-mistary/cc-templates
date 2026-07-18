from types import MappingProxyType

from cc.enums import TemplateType

MAP: MappingProxyType[TemplateType, str] = MappingProxyType(
    {
        TemplateType.scratch: "/scratch",
        TemplateType.cli: "/cli",
    }
)
