from markdown_it import MarkdownIt

from markdown_it.common.utils import unescapeAll, escapeHtml
from markdown_it.token import Token

from typing import List
import re

# orig JS: token.info.match(/^graph (?:TB|BT|RL|LR|TD);?$/)
GRAPH_RE = re.compile(r'^graph (TB|BT|RL|LR|TD)?;?$')
CHART_TYPES = ('mermaid', 'gantt', 'sequenceDiagram', 'classDiagram', 'gitGraph')



def mermaid_plugin(md: MarkdownIt):
    """Render fenced code blocks for mermaid diagrams

    Example:

    ```mermaid
    graph LR
      A --- B
    ```

    The plugin does not add the javascript to actually render the mermaid diagram, just wraps the
    diagram in a '<div class="mermaid">...</div>' as needed by mermaid. Add something like the following
    to your page to let mermaid render the diagram:

    ```JS
    <script src="mermaid.js"></script>

    <script type="text/javascript">
    window.addEventListener('load', function(event) {
       mermaid.initialize({ /* mermaid config */ });
    });
    </script>

    See https://mermaid-js.github.io/mermaid/#/usage for more details

    """

    # save it here to play nice with other plugins which also overwrite/extend this rule
    orig_fence = md.renderer.rules['fence']

    # in add_render_rule(), self will be bound to the md.renderer instance
    def mermaid_fence(self, tokens: List[Token], idx: int, options, env):
        token = tokens[idx]
        info = token.info or ''

        if not (info in CHART_TYPES or GRAPH_RE.match(info)):
            return orig_fence(tokens, idx, options, env)

        # If language is a chart type, we do not need to render that but if it is already part of the
        # graph definition, we have to add it
        if info in CHART_TYPES:
            content = token.content.strip()
        else:
            content = info + '\n' + token.content.strip()

        # Also allow \n as an alternative to </br> in labels (needs enablement in the mermaid config)
        content = content.replace('\\n','<br/>')
        content = escapeHtml(content)
        return f'<div class="mermaid">{content}</div>'

    md.add_render_rule('fence', mermaid_fence)
