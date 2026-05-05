import zipfile
import json
import os

class PackageValidator:
    REQUIRED_MANIFEST_FIELDS = ['name', 'version', 'description']

    def validate_zip(self, filepath):
        errors = []
        manifest = {}

        if not os.path.exists(filepath):
            return {'valid': False, 'errors': ['File not found'], 'manifest': {}}

        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                members = zf.namelist()

                if not members:
                    errors.append('ZIP file is empty')
                    return {'valid': False, 'errors': errors, 'manifest': {}}

                for member in members:
                    if '..' in member or os.path.isabs(member):
                        errors.append(f'Path traversal detected: {member}')

                if errors:
                    return {'valid': False, 'errors': errors, 'manifest': {}}

                if 'manifest.json' not in members:
                    errors.append('Missing required manifest.json')
                    return {'valid': False, 'errors': errors, 'manifest': {}}

                try:
                    data = zf.read('manifest.json')
                    manifest = json.loads(data.decode('utf-8'))
                    for field in self.REQUIRED_MANIFEST_FIELDS:
                        if field not in manifest:
                            errors.append(f'Missing required manifest field: {field}')
                    manifest = {
                        k: str(v)[:500]
                        for k, v in manifest.items()
                        if isinstance(k, str) and len(k) < 100
                    }
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    errors.append(f'Invalid manifest.json: {e}')
                    manifest = {}

        except zipfile.BadZipFile:
            errors.append('Invalid zip file')
            return {'valid': False, 'errors': errors, 'manifest': {}}
        except Exception as e:
            errors.append(f'Error reading zip: {e}')
            return {'valid': False, 'errors': errors, 'manifest': {}}

        return {'valid': len(errors) == 0, 'errors': errors, 'manifest': manifest}
