import unittest
from types import SimpleNamespace

from module.blablalink.renew import RenewError, select_login_region, server_from_client
from module.config.server import android_activity, android_package, android_server, to_server


class AndroidServerTest(unittest.TestCase):
    def test_existing_packages_keep_their_servers(self):
        self.assertEqual(to_server('com.proximabeta.nikke'), 'intl')
        self.assertEqual(to_server('com.gamamobi.nikke'), 'tw')
        self.assertEqual(to_server('intl'), 'intl')
        self.assertEqual(to_server('tw'), 'tw')
        # PC 端 hmt 不是安卓包名；to_server 对未知值仍回落国际服。
        self.assertEqual(to_server('hmt'), 'intl')
        self.assertEqual(to_server('unknown.package'), 'intl')
        self.assertEqual(to_server(''), 'intl')

    def test_cn_package_maps_to_cn(self):
        self.assertEqual(to_server('com.tencent.nikke'), 'cn')
        self.assertEqual(to_server('cn'), 'cn')

    def test_default_android_client_stays_international(self):
        config = SimpleNamespace(
            Emulator_PackageName='com.proximabeta.nikke',
            Emulator_PackageOverride=None,
            Emulator_ActivityOverride=None,
        )
        self.assertEqual(android_package(config), 'com.proximabeta.nikke')
        self.assertEqual(android_server(config), 'intl')
        self.assertEqual(android_activity(config), '')

    def test_selecting_cn_package_does_not_require_overrides(self):
        config = SimpleNamespace(
            Emulator_PackageName='com.tencent.nikke',
            Emulator_PackageOverride='',
            Emulator_ActivityOverride='  ',
        )
        self.assertEqual(android_package(config), 'com.tencent.nikke')
        self.assertEqual(android_server(config), 'cn')
        self.assertEqual(android_activity(config), '')

    def test_unknown_override_is_cn_and_known_override_keeps_its_server(self):
        channel = {
            'Emulator': {
                'Emulator': {
                    'PackageName': 'com.proximabeta.nikke',
                    'PackageOverride': 'com.example.nikke.cn',
                    'ActivityOverride': 'com.example.SplashActivity',
                }
            }
        }
        self.assertEqual(android_package(channel), 'com.example.nikke.cn')
        self.assertEqual(android_server(channel), 'cn')
        self.assertEqual(android_activity(channel), 'com.example.SplashActivity')

        tw = SimpleNamespace(
            Emulator_PackageName='com.tencent.nikke',
            Emulator_PackageOverride='com.gamamobi.nikke',
            Emulator_ActivityOverride=None,
        )
        self.assertEqual(android_package(tw), 'com.gamamobi.nikke')
        self.assertEqual(android_server(tw), 'tw')

    def test_pc_client_server_is_not_rewritten(self):
        config = {
            'NKAS': {'Client': {'Platform': 'win'}},
            'PCClient': {'PCClientInfo': {'Client': 'hmt'}},
            'Emulator': {'Emulator': {'PackageName': 'com.tencent.nikke'}},
        }
        self.assertEqual(server_from_client(config), 'hmt')

    def test_adb_server_follows_package_override(self):
        config = {
            'NKAS': {'Client': {'Platform': 'adb'}},
            'PCClient': {'PCClientInfo': {'Client': 'intl'}},
            'Emulator': {
                'Emulator': {
                    'PackageName': 'com.proximabeta.nikke',
                    'PackageOverride': 'com.tencent.nikke',
                }
            },
        }
        self.assertEqual(server_from_client(config), 'cn')

    def test_cn_does_not_use_blablalink_region(self):
        with self.assertRaises(RenewError):
            select_login_region(page=None, server='cn')
        self.assertFalse(select_login_region(page=None, server='intl'))
        self.assertFalse(select_login_region(page=None, server=''))
