import inspect
import pkgutil

from app.task.runner.models.base import Action
from app.task.runner.registry import ActionRegistry
from app.task.runner.runner import ActionRunner


def build_action_runner() -> ActionRunner:
    registry = ActionRegistry()
    register_action(registry)
    return ActionRunner(registry)

def register_action(registry: ActionRegistry):
    # 通过扫描 models包，加载并注册所有的自定义Action
    # 1.加载models包
    import importlib
    package = importlib.import_module("app.task.runner.models")
    # 2.迭代models包中的组件（子包、模块）
    for __, module_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
        if is_pkg:
            continue
        # 3.加载models包中的模块
        module = importlib.import_module(module_name)
        # 4.获取模块中的成员
        for name, obj in inspect.getmembers(module,inspect.isclass):
            if issubclass(obj,Action) and obj is not Action and obj.__module__ == module.__name__:
                registry.register(obj())
            else:
                continue

if __name__ == '__main__':
    runner = build_action_runner()
    for key,value in runner.registry._actions.items():
        print(key,value)