import builtins
import mmd_tools_tweaks.tw


def register():
    # インタラクティブコンソールの名前空間に追加
    builtins.tw = mmd_tools_tweaks.tw  # type: ignore


def unregister():
    if hasattr(builtins, "tw"):
        del builtins.tw  # type: ignore
