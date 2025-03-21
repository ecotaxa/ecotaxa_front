  import {
    Graph
  } from '@antv/g6';
  import {
    create_box,
    fetchSettings
  } from '../modules/utils.js';
  export function g6_graph(container) {
    const box = create_box('div', {
      id: 'g6-container',
      width: '1500px',
      height: '1500px'
    }, container);
    console.log('container hierachy', box)
    fetch('gui/taxonomy/graph', fetchSettings())
      .then(res => {
        if (res.ok) return res.json();
        else return Promise.reject(res);
      })
      .then((data) => {
        //  console.log('data', data)
        const graph = new Graph({
          container: box.id,
          autoFit: 'view',
          data,
          node: {
            type: 'circle',
            size: 1,
          },
          edge: {
            style: {
              lineWidth: 1,
              color: "#333333"
            }
          },
          layout: {
            type: 'd3-force',
            animate: false,
          },
          modes: {
            default: [{
              type: 'drag-canvas',
              enableOptimize: true,
              // ... other configurations
            }, {
              type: 'zoom-canvas',
              enableOptimize: true,
              // ... other configurations
            }]
          }

        });

        graph.render();
      });
  }