import mara_markdown_docs.config
import mara_app.app
import mara_page.acl
import pathlib
from mara_app.monkey_patch import patch


import pytest


# Workaround for https://github.com/mara/mara-page/pull/6
@patch(mara_page.acl.current_user_has_permissions)
def fixed_current_user_has_permissions(resources):
    return list(map(lambda resource: [resource, True], resources))

repo_root_dir = pathlib.Path(__file__).parent.parent
repo_readme = repo_root_dir / 'README.md'

def _client():

    @patch(mara_markdown_docs.config.documentation)
    def documentation() -> dict:
        """This is a test docstring"""


        # Cases matter in path!
        docs = {
            'xyz_Marketing_xyz': repo_root_dir / 'app/pipelines/marketing/README.md',
            'Developer/Setup': repo_readme,
            'Developer/Code Conventions': repo_root_dir / 'code_conventions.md',
            'test': repo_root_dir / 'tests/docs/test.md'
        }

        return docs

    flask_app = mara_app.app.MaraApp()

    with flask_app.test_client() as client:
        flask_app.testing = True
        yield client

client = pytest.fixture(_client)

def test_redirect_to_full_url(client):
    r = client.get('/docs/developer')
    print(r.data)
    assert b'/docs/developer/' in r.data, 'no redirect'
    assert b'Redirect' in r.data, 'no redirect'
    assert r.status_code == 308, 'No redirect: status'


def test_docs_in_menu(client):
    r = client.get('/mara-app/navigation-bar')
    print(r.data)
    assert b'>Developer</' in r.data, 'Missing folder structure'
    assert b'xyz_Marketing_xyz' in r.data, 'missing entry'
    assert b'href="/docs/developer/code_conventions/"' in r.data, 'missing URL'
    assert b'href="/mara-app/configuration#mara_markdown_docs.config"' in r.data, 'missing entry for config'


def test_docs_in_config(client):
    r = client.get('/mara-app/configuration')
    print(r.data)
    assert b'id="mara_markdown_docs.config"' in r.data, 'Missing config section'
    assert str(repo_readme).encode('utf8') in r.data, 'missing repo readme entry'

def test_doc(client):
    r = client.get('/docs/developer/setup/')
    print(r.data)
    assert b'mara-markdown-docs.git' in r.data, 'Missing link to repo'

def test_overview(client):
    r = client.get('/docs/')
    print(r.data)
    assert b'xyz_Marketing_xyz' in r.data, 'missing entry'
    assert b'href="/docs/developer/code_conventions/"' in r.data, 'missing URL'


def test_404_directory(client):
    r = client.get('/docs/developer/')
    print(r.data)
    assert b'404' in r.data, 'Missing page is not missing'
    assert r.status_code == 404, 'Missing page is not missing: status'


def test_404_page(client):
    r = client.get('/docs/developer/missing/')
    print(r.data)
    assert b'404' in r.data, 'Missing page is not missing'
    assert r.status_code == 404, 'Missing page is not missing: status'

def test_docs_file_endpoint(client):
    r = client.get('/docs/test/test.txt')
    print(r.data)
    assert b'$Test doc$' in r.data
    assert r.status_code == 200

def test_docs_file_endpoint_404(client):
    r = client.get('/docs/test/test2.txt')
    print(r.data)
    assert r.status_code == 404

def test_docs_file_endpoint_dot_dot(client):
    # flask prevents / in the last segment, so this also guards against ..
    r = client.get('/docs/test/../docs/test.txt')
    print(r.data)
    assert r.status_code == 404

def test_docs_file_endpoint_subfolder(client):
    # flask prevents / in the last segment, so also no subfolder
    r = client.get('/docs/test/docs/test.txt')
    print(r.data)
    assert r.status_code == 404

def test_docs_file_endpoint_not_allowed_filetype(client):
    r = client.get('/docs/test/secrets.conf')
    print(r.data)
    assert b'$secrets$' not in r.data
    assert r.status_code == 405

@pytest.fixture
def client_unauth():
    import mara_page.acl
    import mara_markdown_docs.docs
    orig_func = mara_page.acl.current_user_has_permissions

    @patch(mara_page.acl.current_user_has_permissions)
    def current_user_has_permissions(resources):
        def _exclude_docs(resource):
            if resource is mara_markdown_docs.docs.documentation_acl_resource:
                return [resource, False]
            return [resource, True]
        return list(map(_exclude_docs, resources))

    yield from _client()

    patch(mara_page.acl.current_user_has_permissions)(orig_func)

def test_unauth_docs(client_unauth):
    r = client_unauth.get('/docs/developer/setup')
    assert r.status_code == 403, 'Forbidden page is not forbidden'
    r = client_unauth.get('/docs/')
    assert r.status_code == 403, 'Forbidden page is not forbidden'
    r = client_unauth.get('/mara-app/configuration')
    assert r.status_code == 200, 'config should still be allowed'

