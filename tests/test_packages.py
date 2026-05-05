import io
import json
import zipfile
from workforce_devhub.blueprints.packages.routes import _validate_package_zip
import os


VALID_MANIFEST = {
    'package_key': 'test-pkg-v1',
    'name': 'Test Package',
    'version': '1.0.0',
    'description': 'A test package',
    'target_project': 'devhub',
    'intended_paths': ['workforce_devhub/plugins/test.py'],
    'install_steps': ['copy files'],
    'rollback_notes': 'delete copied files',
    'risk_level': 'low',
    'requires_manual_review': True,
}


def _make_zip(manifest=None, extra_files=None, manifest_path='devhub-package.json'):
    """Create an in-memory zip for testing."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        if manifest is not None:
            zf.writestr(manifest_path, json.dumps(manifest))
        if extra_files:
            for name, content in extra_files.items():
                zf.writestr(name, content)
    buf.seek(0)
    return buf.read()


def test_valid_package(tmp_path):
    zip_bytes = _make_zip(manifest=VALID_MANIFEST)
    zip_path = str(tmp_path / 'valid.zip')
    with open(zip_path, 'wb') as f:
        f.write(zip_bytes)
    manifest, errors = _validate_package_zip(zip_path)
    assert errors == []
    assert manifest['name'] == 'Test Package'


def test_missing_manifest(tmp_path):
    zip_bytes = _make_zip(manifest=None)
    zip_path = str(tmp_path / 'no_manifest.zip')
    with open(zip_path, 'wb') as f:
        f.write(zip_bytes)
    manifest, errors = _validate_package_zip(zip_path)
    assert any('manifest' in e.lower() for e in errors)


def test_missing_manifest_keys(tmp_path):
    partial = {'name': 'Partial', 'version': '1.0.0'}
    zip_bytes = _make_zip(manifest=partial)
    zip_path = str(tmp_path / 'partial.zip')
    with open(zip_path, 'wb') as f:
        f.write(zip_bytes)
    manifest, errors = _validate_package_zip(zip_path)
    assert any('Missing manifest keys' in e for e in errors)


def test_path_traversal_in_zip_entries(tmp_path):
    zip_bytes = _make_zip(manifest=VALID_MANIFEST, extra_files={'../evil.py': 'evil'})
    zip_path = str(tmp_path / 'traversal.zip')
    with open(zip_path, 'wb') as f:
        f.write(zip_bytes)
    manifest, errors = _validate_package_zip(zip_path)
    assert any('traversal' in e.lower() or '..' in e for e in errors)


def test_path_traversal_in_intended_paths(tmp_path):
    bad_manifest = dict(VALID_MANIFEST)
    bad_manifest['intended_paths'] = ['../../etc/passwd']
    zip_bytes = _make_zip(manifest=bad_manifest)
    zip_path = str(tmp_path / 'bad_paths.zip')
    with open(zip_path, 'wb') as f:
        f.write(zip_bytes)
    manifest, errors = _validate_package_zip(zip_path)
    assert any('traversal' in e.lower() or '..' in e for e in errors)


def test_not_a_zip(tmp_path):
    path = str(tmp_path / 'notazip.zip')
    with open(path, 'wb') as f:
        f.write(b'not a zip file')
    manifest, errors = _validate_package_zip(path)
    assert errors


def test_upload_valid_package(auth_client, app):
    zip_bytes = _make_zip(manifest=VALID_MANIFEST)
    data = {
        'package_file': (io.BytesIO(zip_bytes), 'test-pkg.zip'),
    }
    resp = auth_client.post(
        '/packages/upload',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b'validated' in resp.data or b'Test Package' in resp.data


def test_upload_invalid_package(auth_client, app):
    zip_bytes = _make_zip(manifest=None)
    data = {
        'package_file': (io.BytesIO(zip_bytes), 'invalid.zip'),
    }
    resp = auth_client.post(
        '/packages/upload',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b'error' in resp.data.lower() or b'Validation' in resp.data
