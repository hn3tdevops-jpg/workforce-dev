import os
import io
import json
import zipfile
import pytest
from devhub.package_validator import PackageValidator

def make_zip(tmp_path, name, members):
    """Create a zip file with given members dict {filename: content_bytes}."""
    zpath = tmp_path / name
    with zipfile.ZipFile(str(zpath), 'w') as zf:
        for fname, content in members.items():
            zf.writestr(fname, content)
    return str(zpath)

def test_missing_file():
    v = PackageValidator()
    result = v.validate_zip('/nonexistent/file.zip')
    assert result['valid'] is False
    assert 'File not found' in result['errors']

def test_invalid_zip(tmp_path):
    bad = tmp_path / 'bad.zip'
    bad.write_bytes(b'not a zip')
    v = PackageValidator()
    result = v.validate_zip(str(bad))
    assert result['valid'] is False
    assert any('Invalid zip' in e for e in result['errors'])

def test_valid_zip_with_manifest(tmp_path):
    manifest = {'name': 'pkg', 'version': '1.0', 'description': 'Test package'}
    zpath = make_zip(tmp_path, 'pkg.zip', {'manifest.json': json.dumps(manifest)})
    v = PackageValidator()
    result = v.validate_zip(zpath)
    assert result['valid'] is True
    assert result['manifest']['name'] == 'pkg'

def test_zip_missing_manifest_fields(tmp_path):
    manifest = {'name': 'pkg'}  # missing version and description
    zpath = make_zip(tmp_path, 'pkg.zip', {'manifest.json': json.dumps(manifest)})
    v = PackageValidator()
    result = v.validate_zip(zpath)
    assert result['valid'] is False
    assert any('version' in e for e in result['errors'])

def test_zip_invalid_manifest_json(tmp_path):
    zpath = make_zip(tmp_path, 'pkg.zip', {'manifest.json': b'not json'})
    v = PackageValidator()
    result = v.validate_zip(zpath)
    assert result['valid'] is False
    assert any('Invalid manifest' in e for e in result['errors'])

def test_zip_path_traversal(tmp_path):
    zpath = tmp_path / 'trav.zip'
    with zipfile.ZipFile(str(zpath), 'w') as zf:
        zf.writestr('../evil.txt', 'evil')
    v = PackageValidator()
    result = v.validate_zip(str(zpath))
    assert result['valid'] is False
    assert any('traversal' in e for e in result['errors'])

def test_empty_zip(tmp_path):
    zpath = make_zip(tmp_path, 'empty.zip', {})
    v = PackageValidator()
    result = v.validate_zip(zpath)
    assert result['valid'] is False
    assert any('empty' in e.lower() for e in result['errors'])

def test_zip_missing_manifest(tmp_path):
    zpath = make_zip(tmp_path, 'nomanifest.zip', {'data.txt': b'hello'})
    v = PackageValidator()
    result = v.validate_zip(zpath)
    assert result['valid'] is False
    assert any('manifest.json' in e for e in result['errors'])

def test_zip_absolute_path(tmp_path):
    zpath = tmp_path / 'abs.zip'
    with zipfile.ZipFile(str(zpath), 'w') as zf:
        zf.writestr('/etc/evil.txt', 'evil')
    v = PackageValidator()
    result = v.validate_zip(str(zpath))
    assert result['valid'] is False
    assert any('traversal' in e or 'Path' in e for e in result['errors'])
