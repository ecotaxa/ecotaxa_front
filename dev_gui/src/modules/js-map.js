'use strict';
import DOMPurify from 'dompurify';
import {
  fetchSettings,
  html_spinner
} from '../modules/utils.js';
// Global map of samples, OpenLayers full build loaded from cdnjs
const OL_URL = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/10.6.1/';
// polar projections definitions for OpenLayers
const PROJ4_URL = 'https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.22.0/proj4.min.js';
const TILES_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer';
// NASA GIBS polar basemaps
const GIBS_URL = 'https://gibs.earthdata.nasa.gov/wmts/';
const POLAR_EXTENT = [-4194304, -4194304, 4194304, 4194304];
const POLAR = {
  north: {
    code: 'EPSG:3413',
    def: '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
    gibs: 'epsg3413',
    // samples of the hemisphere
    visible: (lat) => lat > 0
  },
  south: {
    code: 'EPSG:3031',
    def: '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
    gibs: 'epsg3031',
    visible: (lat) => lat < 0
  }
};
const loadings = {};

function load_script(url) {
  if (loadings[url]) return loadings[url];
  loadings[url] = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = url;
    script.onload = () => resolve();
    script.onerror = () => {
      delete loadings[url];
      reject();
    };
    document.head.append(script);
  });
  return loadings[url];
}

async function load_ol() {
  if (window.ol) return window.ol;
  if (!loadings[OL_URL + 'dist/ol.js']) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = OL_URL + 'ol.css';
    document.head.append(link);
  }
  await load_script(OL_URL + 'dist/ol.js');
  return window.ol;
}

async function load_polar(ol) {
  if (ol.proj.get(POLAR.north.code)) return;
  await load_script(PROJ4_URL);
  Object.values(POLAR).forEach(polar => window.proj4.defs(polar.code, polar.def));
  ol.proj.proj4.register(window.proj4);
}

function polar_source(ol, polar) {
  return new ol.source.XYZ({
    attributions: 'Imagery © <a href="https://earthdata.nasa.gov/gibs">NASA EOSDIS GIBS</a>',
    projection: polar.code,
    tileGrid: new ol.tilegrid.TileGrid({
      extent: POLAR_EXTENT,
      origin: [POLAR_EXTENT[0], POLAR_EXTENT[3]],
      resolutions: [8192, 4096, 2048, 1024, 512],
      tileSize: 512
    }),
    url: GIBS_URL + polar.gibs + '/best/BlueMarble_ShadedRelief_Bathymetry/default/500m/{z}/{y}/{x}.jpeg'
  });
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
  const world_source = new ol.source.XYZ({
    attributions: 'Tiles © <a href="' + TILES_URL + '">ArcGIS</a>',
    url: TILES_URL + '/tile/{z}/{y}/{x}'
  });
  const base = new ol.layer.Tile({
    source: world_source
  });
  const map = new ol.Map({
    target: item,
    layers: [
      base,
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
  // redraws the selected samples, after a change of projection
  let refresh_selection = () => {};
  if (item.dataset.projects) refresh_selection = select_samples(ol, map, samples, item);
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
    lonlat: [sam.long, sam.lat],
    sampleid: sam.id,
    projid: sam.projid
  })));
  // once loaded, the whole world width fills the map width
  function fit_width() {
    if (!item.dataset.fitwidth) return;
    map.updateSize();
    const size = map.getSize();
    if (size && size[0] > 0) map.getView().setResolution(ol.extent.getWidth(ol.proj.get('EPSG:3857').getExtent()) / size[0]);
  }
  fit_width();
  if (item.dataset.views) views_switch(ol, map, base, world_source, samples, item, fit_width, refresh_selection);
  map.getViewport().classList.remove('opacity-50');
  loading.remove();
}

// world or polar views, the samples are displayed in the projection of the view
function views_switch(ol, map, base, world_source, samples, item, fit_width, refresh_selection) {
  const sources = {
    world: world_source
  };
  const control = document.createElement('div');
  control.className = 'absolute top-9 right-2 z-10 flex rounded shadow-sm bg-white text-sm overflow-hidden';
  item.append(control);
  // [[name, label], ...]
  const labels = JSON.parse(item.dataset.views);
  function active(button, on) {
    button.classList.toggle('bg-mainblue-700', on);
    button.classList.toggle('text-white', on);
    button.classList.toggle('hover:bg-stone-100', !on);
  }
  async function set_view(name, button) {
    let projection = 'EPSG:3857';
    if (name !== 'world') {
      try {
        await load_polar(ol);
      } catch (err) {
        return;
      }
      const polar = POLAR[name];
      projection = polar.code;
      if (!sources[name]) sources[name] = polar_source(ol, polar);
    }
    control.querySelectorAll('button').forEach(btn => active(btn, btn === button));
    base.setSource(sources[name]);
    map.setView(new ol.View({
      projection: projection,
      center: [0, 0]
    }));
    samples.getFeatures().forEach(f => {
      const lonlat = f.get('lonlat');
      const visible = name === 'world' || POLAR[name].visible(lonlat[1]);
      f.setGeometry(visible ? new ol.geom.Point(ol.proj.fromLonLat(lonlat, projection)) : undefined);
    });
    refresh_selection();
    if (name === 'world') fit_width();
    else map.getView().fit(POLAR_EXTENT);
  }
  labels.forEach(([name, label]) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'px-2 py-1';
    button.textContent = label;
    active(button, name === 'world');
    button.addEventListener('click', () => set_view(name, button));
    control.append(button);
  });
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
  function redraw() {
    selected.clear();
    selected.addFeatures(Array.from(selection.values()).map(f => f.clone()));
  }
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
    redraw();
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
  return redraw;
}

export {
  JsMap
}
