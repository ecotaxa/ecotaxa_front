'use strict';
import DOMPurify from 'dompurify';
import {
  fetchSettings,
  html_spinner
} from '../modules/utils.js';
// Global map of samples, OpenLayers full build loaded from cdnjs
const OL_URL = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/10.6.1/';
const TILES_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer';
let ol_loading = null;

function load_ol() {
  if (window.ol) return Promise.resolve(window.ol);
  if (ol_loading) return ol_loading;
  ol_loading = new Promise((resolve, reject) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = OL_URL + 'ol.css';
    document.head.append(link);
    const script = document.createElement('script');
    script.src = OL_URL + 'dist/ol.js';
    script.onload = () => resolve(window.ol);
    script.onerror = () => {
      ol_loading = null;
      reject();
    };
    document.head.append(script);
  });
  return ol_loading;
}

async function JsMap(item) {
  if (item.jsmap) return;
  item.jsmap = true;
  // the map is dimmed with a loading icon over it until its samples are displayed
  const loading = document.createElement('div');
  loading.className = 'absolute inset-0 z-10 flex items-center justify-center pointer-events-none';
  loading.innerHTML = html_spinner('text-stone-700', 'h-10 w-10');
  item.append(loading);
  let ol;
  try {
    ol = await load_ol();
  } catch (err) {
    item.textContent = item.dataset.nomap;
    return;
  }
  const samples = new ol.source.Vector();
  const map = new ol.Map({
    target: item,
    layers: [
      new ol.layer.Tile({
        source: new ol.source.XYZ({
          attributions: 'Tiles © <a href="' + TILES_URL + '">ArcGIS</a>',
          url: TILES_URL + '/tile/{z}/{y}/{x}'
        })
      }),
      new ol.layer.Vector({
        source: samples,
        style: new ol.style.Style({
          image: new ol.style.Icon({
            anchor: [0.5, 0.5],
            size: [40, 40],
            offset: [52, 0],
            opacity: 1,
            scale: 0.19,
            src: '/static/dots.png'
          })
        })
      })
    ],
    controls: ol.control.defaults.defaults({
      attributionOptions: {
        collapsible: false
      }
    }).extend([new ol.control.MousePosition({
      coordinateFormat: ol.coordinate.createStringXY(4),
      projection: 'EPSG:4326'
    })]),
    view: new ol.View({
      center: [0, 47],
      // whole height at scale 1 for a 450px high map
      zoom: item.clientHeight / 450
    })
  });
  map.getViewport().classList.add('opacity-50');
  if (item.dataset.projects) select_samples(ol, map, samples, item);
  else popover(ol, map, item);
  let data = [];
  try {
    const response = await fetch(item.dataset.samples, fetchSettings());
    if (response.ok) data = await response.json();
  } catch (err) {
    // the map is displayed without samples
  }
  samples.addFeatures(data.map(sam => new ol.Feature({
    geometry: new ol.geom.Point(ol.proj.fromLonLat([sam.long, sam.lat])),
    sampleid: sam.id,
    projid: sam.projid
  })));
  // once loaded, the whole world width fills the map width
  if (item.dataset.fitwidth) {
    map.updateSize();
    const size = map.getSize();
    if (size && size[0] > 0) map.getView().setResolution(ol.extent.getWidth(ol.proj.get('EPSG:3857').getExtent()) / size[0]);
  }
  map.getViewport().classList.remove('opacity-50');
  loading.remove();
}

// sample information on click
function popover(ol, map, item) {
  const popup = document.createElement('div');
  popup.className = 'hidden bg-white text-stone-800 text-xs p-2 rounded shadow-lg whitespace-nowrap';
  const overlay = new ol.Overlay({
    element: popup,
    positioning: 'bottom-center',
    stopEvent: false,
    offset: [0, -8]
  });
  map.addOverlay(overlay);
  map.on('click', async (evt) => {
    const feature = map.forEachFeatureAtPixel(evt.pixel, (f) => f);
    if (!feature) {
      popup.classList.add('hidden');
      return;
    }
    // the event position handles the cyclic world better than the feature one
    overlay.setPosition(evt.coordinate);
    popup.textContent = '…';
    popup.classList.remove('hidden');
    const response = await fetch(item.dataset.popover + feature.get('sampleid'), fetchSettings());
    popup.innerHTML = DOMPurify.sanitize(await response.text());
  });
}

// the projects of the clicked samples are displayed in the target element,
// shift+click adds or removes samples, ctrl+drag selects the samples in a box, a box close button deselects its samples
function select_samples(ol, map, samples, item) {
  const target = document.getElementById(item.dataset.target);
  const selected = new ol.source.Vector();
  map.addLayer(new ol.layer.Vector({
    source: selected,
    style: new ol.style.Style({
      image: new ol.style.Circle({
        radius: 5,
        fill: new ol.style.Fill({
          color: '#dc2626'
        }),
        stroke: new ol.style.Stroke({
          color: '#ffffff',
          width: 1
        })
      })
    })
  }));
  // selected sample features by sample id
  let selection = new Map();
  async function show(features, toggle = false) {
    if (!toggle) selection = new Map();
    features.forEach(f => {
      const sampleid = f.get('sampleid');
      if (toggle && selection.has(sampleid)) selection.delete(sampleid);
      else selection.set(sampleid, f);
    });
    features = Array.from(selection.values());
    selected.clear();
    if (!target) return;
    if (features.length === 0) {
      target.innerHTML = '';
      return;
    }
    selected.addFeatures(features.map(f => f.clone()));
    const fd = new FormData();
    fd.append('samples', features.map(f => f.get('sampleid')).join(','));
    // the images of a single sample are sized for the space available
    fd.append('resultwidth', target.clientWidth);
    fd.append('windowheight', window.innerHeight);
    target.innerHTML = '<div class="w-full flex justify-center py-4">' + html_spinner('text-stone-700', 'h-8 w-8') + '</div>';
    try {
      const response = await fetch(item.dataset.projects, fetchSettings({
        method: 'POST',
        body: fd
      }));
      target.innerHTML = DOMPurify.sanitize(await response.text());
    } catch (err) {
      target.textContent = '';
    }
  }
  // closing a project box deselects its samples
  if (target) target.addEventListener('click', (e) => {
    const close = e.target.closest('[data-closeproject]');
    if (!close) return;
    const projid = parseInt(close.dataset.closeproject);
    selection.forEach((f, sampleid) => {
      if (f.get('projid') === projid) selection.delete(sampleid);
    });
    selected.clear();
    selected.addFeatures(Array.from(selection.values()).map(f => f.clone()));
    const box = close.closest('[data-projid]');
    if (box) box.remove();
  });
  // all the samples under the click, the points overlap a lot
  map.on('click', (evt) => {
    const features = [];
    map.forEachFeatureAtPixel(evt.pixel, (f) => {
      features.push(f);
    }, {
      layerFilter: (layer) => layer.getSource() === samples
    });
    show(features, evt.originalEvent.shiftKey);
  });
  const dragbox = new ol.interaction.DragBox({
    condition: ol.events.condition.platformModifierKeyOnly
  });
  map.addInteraction(dragbox);
  dragbox.on('boxend', () => {
    const features = [];
    samples.forEachFeatureIntersectingExtent(dragbox.getGeometry().getExtent(), (f) => {
      features.push(f);
    });
    show(features);
  });
}

export {
  JsMap
}
