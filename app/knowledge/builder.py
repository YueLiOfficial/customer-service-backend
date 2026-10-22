import inspect
import pkgutil

from app.knowledge.models.providers import KnowledgeProvider
from app.knowledge.registry import ProviderRegistry


def build_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    register_provider(registry)
    return registry

def register_provider(registry: ProviderRegistry):
    # 通过扫描 models包，加载并注册所有的provider
    # 1.加载models包
    import importlib
    package = importlib.import_module("app.knowledge.models")
    # 2.迭代models包中的组件（子包、模块）
    for __, module_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
        if is_pkg:
            continue
        # 3.加载models包中的模块
        module = importlib.import_module(module_name)
        # 4.获取模块中的成员
        for name, obj in inspect.getmembers(module,inspect.isclass):
            if issubclass(obj,KnowledgeProvider) and obj is not KnowledgeProvider and obj.__module__ == module.__name__:
                registry.register(obj())
            else:
                continue

if __name__ == '__main__':
    registry = build_provider_registry()
    for key,value in registry._providers.items():
        print(key,value)