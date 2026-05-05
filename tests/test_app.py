def test_app_creates(app):
    assert app is not None


def test_app_testing_config(app):
    assert app.config['TESTING'] is True
    assert app.config['WTF_CSRF_ENABLED'] is False


def test_blueprints_registered(app):
    blueprint_names = [bp for bp in app.blueprints]
    for name in ['auth', 'main', 'projects', 'docs', 'progress', 'scripts',
                 'packages', 'files', 'search', 'admin', 'api']:
        assert name in blueprint_names, f'Missing blueprint: {name}'
