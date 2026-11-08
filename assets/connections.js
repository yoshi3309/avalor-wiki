(() => {
  'use strict';
  const section = document.querySelector('[data-connection-map]');
  const dataEl = document.getElementById('connection-map-data');
  if (!section || !dataEl) return;
  let graph;
  try { graph = JSON.parse(dataEl.textContent); } catch { return; }
  const nodes = new Map(graph.nodes.map(node => [node.id, node]));
  const buttons = [...section.querySelectorAll('[data-node-id]')];
  const links = [...section.querySelectorAll('.connection-line')];
  const name = section.querySelector('#connection-detail-name');
  const description = section.querySelector('#connection-detail-description');
  const list = section.querySelector('#connection-detail-links');
  const record = section.querySelector('#connection-record-link');
  const root = window.AVALOR_ROOT || '../../';
  const highlight = id => {
    if (!nodes.has(id)) return;
    const node = nodes.get(id);
    buttons.forEach(button => {
      const pressed = button.dataset.nodeId === id;
      button.classList.toggle('is-selected', pressed);
      button.setAttribute('aria-pressed', String(pressed));
      button.classList.toggle('is-connected', graph.edges.some(edge => (edge.from === id && edge.to === button.dataset.nodeId) || (edge.to === id && edge.from === button.dataset.nodeId)));
    });
    links.forEach(line => {
      const related = line.dataset.edgeFrom === id || line.dataset.edgeTo === id;
      line.classList.toggle('is-active', related);
      line.classList.toggle('is-muted', !related);
    });
    name.textContent = node.label;
    description.textContent = node.detail;
    list.replaceChildren();
    const related = graph.edges.filter(edge => edge.from === id || edge.to === id);
    for (const edge of related) {
      const otherId = edge.from === id ? edge.to : edge.from;
      const other = nodes.get(otherId);
      if (!other) continue;
      const item = document.createElement('li');
      const label = document.createElement('span');
      label.textContent = edge.label + ': ';
      item.appendChild(label);
      const select = document.createElement('button');
      select.type = 'button';
      select.textContent = other.label;
      select.addEventListener('click', () => highlight(otherId));
      item.appendChild(select);
      list.appendChild(item);
    }
    record.hidden = !node.article;
    if (node.article) record.href = root + 'articles/' + encodeURIComponent(node.article) + '/';
  };
  buttons.forEach(button => button.addEventListener('click', () => highlight(button.dataset.nodeId)));
  section.querySelectorAll('[data-select-node]').forEach(button => button.addEventListener('click', () => {
    highlight(button.dataset.selectNode);
    section.querySelector('#connection-detail-name')?.scrollIntoView({behavior:'auto',block:'center'});
  }));
  if (graph.nodes.length) highlight(graph.nodes.find(node => node.kind === 'group')?.id || graph.nodes[0].id);
})();
