server = 'intl'

VALID_SERVER = ['intl', 'tw', 'cn']

# 国服官服包名来自腾讯应用宝详情页 https://sj.qq.com/appdetail/com.tencent.nikke
# （胜利女神：新的希望，运营商深圳市腾讯天游科技有限公司）。
# 启动 Activity 没有公开清单，不在这里登记，交给运行时解析或 ActivityOverride。
VALID_PACKAGE = {
    'com.proximabeta.nikke': 'intl',
    'com.gamamobi.nikke': 'tw',
    'com.tencent.nikke': 'cn',
}

DICT_PACKAGE_TO_ACTIVITY = {
    'com.proximabeta.nikke': 'com.shiftup.nk.MainActivity',
}

# 渠道包（TapTap / Bilibili 等）包名未核实，不在这里写死。
# 安卓端用 Emulator.PackageOverride 指向实际包名，未知包名按国服处理。
VALID_CHANNEL_PACKAGE = {

}


def set_server(package_or_server: str):
    """
    Change server and this will effect globally,
    including assets and server specific methods.

    Args:
        package_or_server: package name or server.
    """
    global server
    server = to_server(package_or_server)


def known_server(package_or_server: str):
    """
    Map a package or server id onto intl/tw/cn.
    Return None when the value is not a known package or server id.
    """
    if not package_or_server:
        return None
    if package_or_server in VALID_SERVER:
        return package_or_server
    if package_or_server in VALID_PACKAGE:
        return VALID_PACKAGE[package_or_server]
    if package_or_server in VALID_CHANNEL_PACKAGE:
        entry = VALID_CHANNEL_PACKAGE[package_or_server]
        if isinstance(entry, (list, tuple)) and entry:
            return entry[0]
        if isinstance(entry, str):
            return entry
    return None


def to_server(package_or_server: str) -> str:
    """
    Convert package/server to server.
    To unknown packages, consider they are a intl channel servers.
    """
    return known_server(package_or_server) or 'intl'


def _config_text(config, attr: str, dict_keys: str) -> str:
    if isinstance(config, dict):
        from module.config.deep import deep_get
        value = deep_get(config, dict_keys, default='')
    else:
        value = getattr(config, attr, '')
    if value is None:
        return ''
    return str(value).strip()


def android_package(config) -> str:
    """
    Android/emulator package to launch.
    PackageOverride wins when set; otherwise Emulator.PackageName.
    """
    override = _config_text(config, 'Emulator_PackageOverride', 'Emulator.Emulator.PackageOverride')
    if override:
        return override
    return _config_text(config, 'Emulator_PackageName', 'Emulator.Emulator.PackageName')


def android_activity(config) -> str:
    """
    Optional launcher activity override. Empty means the existing start path
    (registered activity, monkey, or the device's resolved launcher activity).
    """
    return _config_text(config, 'Emulator_ActivityOverride', 'Emulator.Emulator.ActivityOverride')


def android_server(config) -> str:
    """
    Server id for the Android/emulator client.

    A known PackageOverride keeps that package's server. An unknown override
    is 国服: the field exists for CN store channels whose package names are
    not verified. With no override, this is to_server(PackageName), so the
    international and HK/TW packages stay on their existing servers.
    """
    override = _config_text(config, 'Emulator_PackageOverride', 'Emulator.Emulator.PackageOverride')
    if override:
        return known_server(override) or 'cn'
    return to_server(_config_text(config, 'Emulator_PackageName', 'Emulator.Emulator.PackageName'))
