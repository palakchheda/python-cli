import conftest
import os
from pathlib import Path


def read_config():
    with open(f'{conftest.home()}/.britive/pybritive.config', 'r') as f:
        return f.read()


def write_npm_config(simple=True):
    home = conftest.home()
    local_home = os.getenv('PYBRITIVE_HOME_DIR')
    unit = os.getenv('PYBRITIVE_UNIT_TESTING')
    if home and not unit:
        path = Path(Path(local_home) / '.britive' / 'config')

        tenant = os.getenv('PYBRITIVE_TEST_TENANT')
        contents = [
            f'tenantURL = "https://{tenant}.britive-app.com"',
            'output_format = "Table"'
        ]

        alias = os.getenv('PYBRITIVE_NPM_IMPORT_PROFILE_ALIAS_VALUE')
        if not simple and alias:
            contents = [
                f'tenantURL = "https://{tenant}.britive-app.com"',
                'output_format = "Table"',
                '',
                '[envProfileMap]',
                f'testalias = "{alias}"'
            ]

        path.write_text('\n'.join(contents))


def common_asserts(result, substring=None, exit_code=0):
    assert result.exit_code == exit_code
    if substring:
        if isinstance(substring, str):
            substring = [substring]
        data = read_config()
        for sub in substring:
            assert sub in data


def test_configure_tenant_via_flags_no_alias(runner, cli):
    result = runner.invoke(cli, 'configure tenant -t test1 -f yaml'.split(' '))
    common_asserts(result, substring='[tenant-test1]')


def test_configure_tenant_via_flags_no_alias_no_format(runner, cli):
    result = runner.invoke(cli, 'configure tenant -t test2'.split(' '))
    common_asserts(result, substring='[tenant-test2]')


def test_configure_tenant_via_flags_yes_alias(runner, cli):
    result = runner.invoke(cli, 'configure tenant -t test -f yaml -a testalias1'.split(' '))
    common_asserts(result, substring='[tenant-testalias1]')


def test_configure_tenant_via_flags_yes_alias_no_format(runner, cli):
    result = runner.invoke(cli, 'configure tenant -t test -a testalias2'.split(' '))
    common_asserts(result, substring='[tenant-testalias2]')


def test_configure_tenant_via_prompt_no_alias(runner, cli):
    result = runner.invoke(cli, 'configure tenant'.split(' '), input='test3\n\njson\n')
    common_asserts(result, substring='[tenant-test3]')


def test_configure_tenant_via_prompt_no_alias_no_format(runner, cli):
    result = runner.invoke(cli, 'configure tenant'.split(' '), input='test4\n\n\n')
    common_asserts(result, substring='[tenant-test4]')


def test_configure_tenant_via_prompt_yes_alias(runner, cli):
    result = runner.invoke(cli, ['configure', 'tenant'], input='test4\ntestalias3\nyaml\n')
    common_asserts(result, substring='[tenant-testalias3]')


def test_configure_tenant_via_prompt_yes_alias_no_format(runner, cli):
    result = runner.invoke(cli, ['configure', 'tenant'], input='test4\ntestalias4\n\n')
    common_asserts(result, substring='[tenant-testalias4]')


def test_configure_global_via_flags_file_backend(runner, cli):
    result = runner.invoke(cli, 'configure global -t test1 -f table -b file'.split(' '))
    common_asserts(result, substring=['default_tenant=test1', 'output_format=table', 'credential_backend=file'])


def test_configure_global_via_flags_encrypted_file_backend(runner, cli):
    result = runner.invoke(cli, 'configure global -t test2 -f yaml -b encrypted-file'.split(' '))
    common_asserts(
        result,
        substring=[
            'default_tenant=test2',
            'output_format=yaml',
            'credential_backend=encrypted-file'
        ]
    )


def test_configure_global_via_prompt_file_backend(runner, cli):
    result = runner.invoke(cli, 'configure global'.split(' '), input='test1\ntable-pretty\nfile\n')
    common_asserts(result, substring=['default_tenant=test1', 'output_format=table-pretty', 'credential_backend=file'])


def test_configure_global_via_prompt_encrypted_file_backend(runner, cli):
    result = runner.invoke(cli, 'configure global'.split(' '), input='test2\n\nencrypted-file\n')
    common_asserts(
        result,
        substring=[
            'default_tenant=test2',
            'output_format=json',
            'credential_backend=encrypted-file'
        ]
    )


def test_configure_global_with_invalid_format(runner, cli):
    result = runner.invoke(cli, 'configure global -f error -P'.split(' '))
    assert "Invalid value for '--format' / '-f'" in result.output


def test_configure_global_with_invalid_tenant(runner, cli):
    result = runner.invoke(cli, 'configure global -t incorect'.split(' '))
    assert "Invalid global field default_tenant value incorect provided. Tenant not found." in result.output


def test_configure_import_simple(runner, cli):
    write_npm_config(True)
    tenant = os.getenv('PYBRITIVE_TEST_TENANT')
    result = runner.invoke(cli, 'configure import'.split(' '))
    common_asserts(result, substring=[tenant])


def test_configure_import_complex(runner, cli):
    write_npm_config(False)
    tenant = os.getenv('PYBRITIVE_TEST_TENANT')
    result = runner.invoke(cli, 'configure import'.split(' '))
    print(result.output)
    assert f'Found tenant {tenant}.' in result.output
    assert f'Found default output format' in result.output
    assert 'Profile aliases exist...will retrieve profile details from the tenant.' in result.output
    assert 'Saved alias testalias to profile' in result.output
    common_asserts(result, substring=[tenant, '[profile-aliases]', 'testalias='])


def test_configure_update_global_invalid_data(runner, cli):
    result = runner.invoke(cli, 'configure update global default_tenant incorrect'.split(' '))
    assert result.exit_code == 1
    assert 'Invalid global field default_tenant value incorrect provided. Tenant not found.' in result.output


def test_configure_update_invalid_section(runner, cli):
    result = runner.invoke(cli, 'configure update test default_tenant incorrect'.split(' '))
    assert result.exit_code == 1
    assert 'Cannot save config file due to invalid data provided.' in result.output


def test_configure_update_global_correct_data(runner, cli):
    result = runner.invoke(cli, 'configure update global output_format table-presto'.split(' '))
    common_asserts(result, substring=['output_format=table-presto'])


def test_configure_update_tenant_correct_data(runner, cli):
    tenant = os.getenv('PYBRITIVE_TEST_TENANT')
    result = runner.invoke(cli, f'configure update tenant-{tenant} name test'.split(' '))
    common_asserts(result, substring=['name=test'])
    # set it back
    runner.invoke(cli, f'configure update tenant-{tenant} name {tenant}'.split(' '))