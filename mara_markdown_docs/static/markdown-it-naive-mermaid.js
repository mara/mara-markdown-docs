// A really stupid renderer for code blocks to a mermaid div

const NaiveMermaidPlugIn = (md, opts)=> {
  const defaultRenderer = md.renderer.rules.fence.bind(md.renderer.rules);

  md.renderer.rules.fence=(tokens, idx, opts, env, self)=>{
    const token = tokens[idx];
    var x;
    if (token.info === 'mermaid' || token.info === 'gantt' || token.info === 'sequenceDiagram' || token.info === 'classDiagram' || token.info === 'gitGraph') {
       x = `${token.content.trim()}`;
    } else {
       x = `${token.info} \n ${token.content.trim()}`;
    }
    // also recognice \n as a linebreak
    const code = x.replace(/\\n/g,'<br/>');
    if (token.info === 'mermaid' || token.info === 'gantt' || token.info === 'sequenceDiagram' || token.info === 'classDiagram' || token.info === 'gitGraph' || token.info.match(/^graph (?:TB|BT|RL|LR|TD);?$/)) {
        return `<div class="mermaid">${code}</div>`
    }
    return defaultRenderer(tokens, idx, opts, env, self)
  }
}
