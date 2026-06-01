from abc import ABC, abstractmethod
from typing import Any

from core.tools.decision import Decision


class Tool(ABC):
    """工具抽象基类

    所有工具类必须继承此类并实现 schema 和 invoke 方法。

    Attributes:
        schema: 工具的元数据定义，包含名称、描述和输入模式
    """
    @property
    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """定义工具的元数据

        Returns:
            dict: 包含以下键的字典：
                - name (str): 工具名称
                - description (str): 工具描述
                - input_schema (dict): 输入参数的 JSON Schema
        """
        pass

    def check_permission(self,*args: Any, **kwargs: Any):
        """检查当前用户是否具有执行工具的权限

        Returns:
            bool: 如果当前用户有权限，则返回 True，否则返回 False
        """
        return Decision.ALLOW, ""

    @abstractmethod
    def invoke(self,*args: Any, **kwargs: Any) -> Any:
        """执行工具的核心逻辑

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            Any: 工具执行结果（通常为字符串）

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        pass