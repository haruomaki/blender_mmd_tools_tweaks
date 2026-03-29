"""
tw.py
"""


def reload():
    """モジュール群のインポート"""
    import importlib
    import pkgutil
    import sys
    from importlib import import_module

    g = globals()

    package = import_module(__package__)
    for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
        if name == "tw":  # 自分自身はスキップ
            continue

        full_name = f"{__package__}.{name}"
        print("MODULE:", full_name)

        if full_name not in sys.modules:  # 未ロードはreloadじゃなくimport
            mod = import_module(full_name)
        else:
            mod = importlib.reload(sys.modules[full_name])

        # TODO: 関数の削除が反映されない（仕様だからしょうがない？）
        g.update(mod.__dict__)

    print("[MMD Tools Tweaks] modules reloaded")


reload()
