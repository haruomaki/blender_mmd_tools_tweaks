# モジュール群のインポート
def reload():
    import importlib
    from . import mmd, misc, bone, material, transform

    # TODO: 関数の削除が反映されない（仕様だからしょうがない？）
    globals().update(importlib.reload(mmd).__dict__)
    globals().update(importlib.reload(misc).__dict__)
    globals().update(importlib.reload(bone).__dict__)
    globals().update(importlib.reload(material).__dict__)
    importlib.reload(transform)  # グローバル名前空間には持ってこない
    print("[MMD Tools Tweaks] modules reloaded")


reload()
