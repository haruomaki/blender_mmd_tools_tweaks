import builtins
from . import tw


def register():
    # インタラクティブコンソールの名前空間に追加
    # print("registerです")
    builtins.tw = tw


def unregister():
    # print("unregisterです")
    if hasattr(builtins, "tw"):
        del builtins.tw
