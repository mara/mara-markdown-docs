import flask
import pathlib
import dataclasses

from mara_page import navigation, response, _, bootstrap, acl
from markdown_it import MarkdownIt
from markdown_it.extensions.front_matter import front_matter_plugin
from markdown_it.extensions.footnote import footnote_plugin
from markdown_it.extensions.deflist import deflist_plugin
from .mermaid_md_plugin import mermaid_plugin

from .config import documentation

docs = flask.Blueprint('docs', __name__, url_prefix='/docs', static_folder='static')

documentation_acl_resource = acl.AclResource(name='Documentation')


@dataclasses.dataclass
class Doc:
    full_doc_id: str
    full_name: str
    path: pathlib.Path

    @property
    def doc_name(self):
        """The Page title which should show up in the menu"""
        doc_name = self.full_name
        if '/' in self.full_doc_id and '/' in self.full_name:
            _, doc_name = self.full_name.split('/', maxsplit=1)
        return doc_name

    @property
    def folder_name(self):
        """The Name of the Folder this doc is in (or empty for root)"""
        folder_name = ''
        if '/' in self.full_doc_id and '/' in self.full_name:
            folder_name, _ = self.full_name.split('/', maxsplit=1)
        return folder_name

    @property
    def ids(self):
        """The folder_id, doc_id of this doc"""
        folder_id = ''
        doc_id = self.full_doc_id
        if '/' in doc_id:
            folder_id, doc_id = doc_id.split('/', maxsplit=1)
        return folder_id, doc_id


def all_docs():
    all_docs = {}
    for full_name, path in documentation().items():
        if full_name.count('/') > 1:
            raise ValueError(f"Only one folder level allowed: {full_name}")
        full_doc_id = f"{full_name.lower().replace(' ', '_')}"
        all_docs[full_doc_id] = Doc(full_doc_id, full_name, path)
    return all_docs


def documentation_navigation_entry():
    children = []
    folders = {}
    for full_doc_id, doc in all_docs().items():
        where_to_append = children
        folder_id = None
        folder_id, doc_id = doc.ids
        if folder_id:
            folder = folders.get(folder_id)
            if not folder:
                folder = navigation.NavigationEntry(label=doc.folder_name, icon='book',
                                                    description=f"Documentation Folder {doc.folder_name}")
                children.append(folder)
                folders[folder_id] = folder
            where_to_append = folder
        child = navigation.NavigationEntry(
            label=doc.doc_name, icon='file', description=f'Documentation for "{doc.full_name}"',
            uri_fn=lambda _doc_id=doc_id, _folder_id=folder_id: flask.url_for('docs.document',
                                                                              doc_id=_doc_id,
                                                                              folder_id=_folder_id))
        where_to_append.append(child) if isinstance(where_to_append, list) else where_to_append.add_child(child)
    return navigation.NavigationEntry(
        label='Documentation', icon='book', rank=100,
        description='Documentation',
        uri_fn=lambda: flask.url_for('docs.start_page'),
        children=children)


@docs.route('')
@docs.route('/')
@acl.require_permission(documentation_acl_resource)
def start_page():
    links = []
    for full_doc_id, doc in all_docs().items():
        folder_id, doc_id = doc.ids
        links.append(_.li[_.a(href=flask.url_for('docs.document', doc_id=doc_id, folder_id=folder_id))[doc.full_name]])

    return response.Response(title='Docs', html=[
        bootstrap.card(header_left='Table of Content', body=[_.ul[links]])
    ])


@docs.route('/<doc_id>')
@docs.route('/<folder_id>/<doc_id>')
@acl.require_permission(documentation_acl_resource)
def document(doc_id, folder_id=""):
    docs = all_docs()
    if folder_id:
        full_doc_id = folder_id + '/' + doc_id
    else:
        full_doc_id = doc_id
    if full_doc_id not in docs:
        raise flask.abort(404, f"Documentation {doc_id} is not known.")
    doc = docs[full_doc_id]
    if not doc.path.exists():
        raise flask.abort(404, f"Documentation {doc_id} is not found ({doc.path}).")
    with doc.path.open() as f:
        md_content = f.read()

        # style tables with bootstrap
        def render_table_open(self, tokens, idx, options, env):
            return '<table class="table">'

        md = (
            MarkdownIt()
                .use(front_matter_plugin)
                .use(footnote_plugin)
                .use(deflist_plugin)
                .use(mermaid_plugin)
                .enable('table')
        )
        md.add_render_rule("table_open", render_table_open)

        html_text = md.render(md_content)

        return response.Response(
            title=f'Doc "{doc.full_name}"',
            html=[bootstrap.card(
                body=[
                    _.div(id_='markdown-rendered-content')[html_text],
                ]),
                _.script(type="text/javascript")[__mermaid_render_code],
            ],
            js_files=[
                'https://cdnjs.cloudflare.com/ajax/libs/mermaid/8.7.0/mermaid.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.10/highlight.min.js',
            ],
            css_files=[
                'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.10/styles/default.min.css',
            ]
        )


# language=JavaScript
__mermaid_render_code = """
window.addEventListener('load', function(event) {
mermaid.initialize({
  // allow html tags in text
  securityLevel: 'loose',
  flowchart:{
            // don't go over the surrounding container
            useMaxWidth:true,
            // allow html in labels
            htmlLabels:true
        }
  });
});
"""
