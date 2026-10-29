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
// land and countries of Natural Earth, as vectors so that they can be drawn in any projection
const WORLD_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json';
const WORLD_ATTRIBUTION = '© <a href="https://www.naturalearthdata.com">Natural Earth</a>';
const COLORS = {
  ocean: '#dbeafe',
  land: '#e7e5e4',
  border: '#a8a29e',
  graticule: 'rgba(87,83,78,0.35)'
};
// round polar maps, from the pole down to the edge latitude
const POLAR = {
  north: {
    code: 'EPSG:3413',
    def: '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
    edge: 40,
    // samples displayed in the disk
    visible: (lat) => lat >= 40
  },
  south: {
    code: 'EPSG:3031',
    def: '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
    edge: -40,
    visible: (lat) => lat <= -40
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
  Object.values(POLAR).forEach(polar => {
    // distance from the pole to the edge latitude, the graticule needs the extents
    const edge = ol.proj.fromLonLat([0, polar.edge], polar.code);
    polar.radius = Math.hypot(edge[0], edge[1]);
    const projection = ol.proj.get(polar.code);
    projection.setExtent([-polar.radius, -polar.radius, polar.radius, polar.radius]);
    projection.setWorldExtent(polar.edge > 0 ? [-180, polar.edge, 180, 90] : [-180, -90, 180, polar.edge]);
  });
}

function load_world() {
  if (!loadings[WORLD_URL]) {
    loadings[WORLD_URL] = fetch(WORLD_URL).then(response => {
      if (!response.ok) throw new Error(response.statusText);
      return response.json();
    }).catch(err => {
      delete loadings[WORLD_URL];
      return null;
    });
  }
  return loadings[WORLD_URL];
}

// world-atlas polygons are spherical (d3-geo): rings cross the antimeridian and Antarctica goes around the pole.
// They are made planar in lon/lat before projection: continuous longitudes, rings around a pole closed through it.
function unwrap(coords) {
  const out = [coords[0].slice()];
  for (let i = 1; i < coords.length; i++) {
    let lon = coords[i][0];
    const prev = out[i - 1][0];
    while (lon - prev > 180) lon -= 360;
    while (lon - prev < -180) lon += 360;
    out.push([lon, coords[i][1]]);
  }
  return out;
}

function is_pole_ring(ring) {
  return ring.every(p => Math.abs(p[1]) > 89.9);
}

function close_ring(ring, pole_lat) {
  const first = ring[0];
  const last = ring[ring.length - 1];
  if (Math.abs(last[0] - first[0]) < 180) return ring;
  // went once around the pole of its hemisphere
  const pole = ring.reduce((sum, p) => sum + p[1], 0) < 0 ? -pole_lat : pole_lat;
  return ring.slice(0, -1).concat([
    [last[0], pole],
    [first[0], pole], first.slice()
  ]);
}

// part of the ring on the polar side of the cut latitude, null if none
function clip_ring(ring, inside, cut) {
  const out = [];
  const cross = (a, b) => [a[0] + (cut - a[1]) / (b[1] - a[1]) * (b[0] - a[0]), cut];
  for (let i = 0; i < ring.length - 1; i++) {
    const a = ring[i];
    const b = ring[i + 1];
    if (inside(a)) out.push(a);
    if (inside(a) !== inside(b)) out.push(cross(a, b));
  }
  if (out.length < 3) return null;
  out.push(out[0].slice());
  // along the cut, follow the parallel: a straight line in polar projection would cross the disk
  const dense = [out[0]];
  for (let i = 1; i < out.length; i++) {
    const a = out[i - 1];
    const b = out[i];
    if (a[1] === cut && b[1] === cut) {
      const steps = Math.floor(Math.abs(b[0] - a[0]));
      for (let s = 1; s < steps; s++) dense.push([a[0] + (b[0] - a[0]) * s / steps, cut]);
    }
    dense.push(b);
  }
  return dense;
}

function clip_line(line, inside, cut) {
  const parts = [];
  let part = [];
  const cross = (a, b) => [a[0] + (cut - a[1]) / (b[1] - a[1]) * (b[0] - a[0]), cut];
  line.forEach((b, i) => {
    const a = line[i - 1];
    if (a && inside(a) !== inside(b)) part.push(cross(a, b));
    if (inside(b)) part.push(b);
    else if (part.length) {
      parts.push(part);
      part = [];
    }
  });
  if (part.length) parts.push(part);
  return parts.filter(p => p.length > 1);
}

// land and countries borders, in lon/lat
let world_features = null;

// land and countries borders in the projection of the view, polar ones are cut a bit beyond the edge of the disk
function world_source(ol, world, projection, polar = null) {
  const source = new ol.source.Vector({
    attributions: WORLD_ATTRIBUTION
  });
  if (!world) return source;
  if (!world_features) world_features = new ol.format.TopoJSON({
    layerName: 'layer',
    layers: ['land', 'countries']
  }).readFeatures(world);
  let inside = () => true;
  let cut = 0;
  if (polar) {
    cut = polar.edge + (polar.edge > 0 ? -5 : 5);
    inside = polar.edge > 0 ? (p) => p[1] >= cut : (p) => p[1] <= cut;
  }
  // mercator stops before the poles
  const pole_lat = polar ? 90 : 85;
  const polygons = [];
  const lines = [];
  world_features.forEach(feature => {
    const geometry = feature.getGeometry();
    const coords = geometry.getType() === 'Polygon' ? [geometry.getCoordinates()] : geometry.getCoordinates();
    coords.forEach(polygon => {
      const rings = polygon.filter(ring => !is_pole_ring(ring)).map(unwrap);
      if (feature.get('layer') === 'land') {
        const clipped = rings.map(ring => close_ring(ring, pole_lat)).map(ring => (polar ? clip_ring(ring, inside, cut) : ring));
        // without its exterior ring, nothing left of the polygon
        if (clipped.length && clipped[0]) polygons.push(clipped.filter(ring => ring));
      } else {
        rings.forEach(ring => lines.push(...(polar ? clip_line(ring, inside, cut) : [ring])));
      }
    });
  });
  const land = new ol.Feature(new ol.geom.MultiPolygon(polygons).transform('EPSG:4326', projection));
  land.set('layer', 'land');
  const borders = new ol.Feature(new ol.geom.MultiLineString(lines).transform('EPSG:4326', projection));
  borders.set('layer', 'borders');
  source.addFeatures([land, borders]);
  return source;
}

// the sea under the land: the whole world, or the polar disk
function ocean_source(ol, polar) {
  const geometry = polar ? new ol.geom.Circle([0, 0], polar.radius) : ol.geom.Polygon.fromExtent(ol.proj.get('EPSG:3857').getExtent());
  return new ol.source.Vector({
    features: [new ol.Feature(geometry)]
  });
}

// polar views are round: the layers drawn beyond the edge latitude are cut out
function clip_to_disk(ol, map, layer, disk) {
  layer.on('prerender', (evt) => {
    if (!disk.radius) return;
    const ctx = evt.context;
    const center = ol.render.getRenderPixel(evt, map.getPixelFromCoordinate([0, 0]));
    const edge = ol.render.getRenderPixel(evt, map.getPixelFromCoordinate([disk.radius, 0]));
    ctx.save();
    ctx.beginPath();
    ctx.arc(center[0], center[1], Math.hypot(edge[0] - center[0], edge[1] - center[1]), 0, 2 * Math.PI);
    ctx.clip();
  });
  layer.on('postrender', (evt) => {
    if (disk.radius) evt.context.restore();
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
  const world = load_world();
  const ocean = new ol.layer.Vector({
    source: ocean_source(ol, null),
    style: new ol.style.Style({
      fill: new ol.style.Fill({
        color: COLORS.ocean
      })
    })
  });
  const land_style = new ol.style.Style({
    fill: new ol.style.Fill({
      color: COLORS.land
    })
  });
  const border_style = new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: COLORS.border,
      width: 0.5
    })
  });
  const land = new ol.layer.Vector({
    source: new ol.source.Vector(),
    style: (feature) => (feature.get('layer') === 'land' ? land_style : border_style)
  });
  const graticule = new ol.layer.Graticule({
    strokeStyle: new ol.style.Stroke({
      color: COLORS.graticule,
      width: 0.5,
      lineDash: [2, 4]
    }),
    wrapX: false
  });
  const map = new ol.Map({
    target: item,
    layers: [
      ocean,
      land,
      graticule,
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
  // radius of the round polar view, none for the world
  const disk = {
    radius: null
  };
  clip_to_disk(ol, map, land, disk);
  clip_to_disk(ol, map, graticule, disk);
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
  // without the world data, the samples are displayed on the sea only
  const world_data = await world;
  land.setSource(world_source(ol, world_data, 'EPSG:3857'));
  // once loaded, the whole world width fills the map width
  function fit_width() {
    if (!item.dataset.fitwidth) return;
    map.updateSize();
    const size = map.getSize();
    if (size && size[0] > 0) map.getView().setResolution(ol.extent.getWidth(ol.proj.get('EPSG:3857').getExtent()) / size[0]);
  }
  fit_width();
  if (item.dataset.views) views_switch(ol, map, {
    ocean: ocean,
    land: land
  }, world_data, disk, samples, item, fit_width, refresh_selection);
  map.getViewport().classList.remove('opacity-50');
  loading.remove();
}

// world or polar views, the samples are displayed in the projection of the view
// polar views are round, from the pole to the edge latitude
function views_switch(ol, map, layers, world_data, disk, samples, item, fit_width, refresh_selection) {
  // ocean and land sources by view, the land features are read once for each projection
  const sources = {
    world: {
      ocean: layers.ocean.getSource(),
      land: layers.land.getSource()
    }
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
    let polar = null;
    if (name !== 'world') {
      try {
        await load_polar(ol);
      } catch (err) {
        return;
      }
      polar = POLAR[name];
      projection = polar.code;
      if (!sources[name]) sources[name] = {
        ocean: ocean_source(ol, polar),
        land: world_source(ol, world_data, projection, polar)
      };
    }
    control.querySelectorAll('button').forEach(btn => active(btn, btn === button));
    disk.radius = polar ? polar.radius : null;
    layers.ocean.setSource(sources[name].ocean);
    layers.land.setSource(sources[name].land);
    const disk_extent = polar ? [-polar.radius, -polar.radius, polar.radius, polar.radius] : undefined;
    map.setView(new ol.View({
      projection: projection,
      center: [0, 0],
      // the polar disk can't be dragged out of sight
      extent: disk_extent,
      constrainOnlyCenter: true
    }));
    samples.getFeatures().forEach(f => {
      const lonlat = f.get('lonlat');
      const visible = name === 'world' || POLAR[name].visible(lonlat[1]);
      f.setGeometry(visible ? new ol.geom.Point(ol.proj.fromLonLat(lonlat, projection)) : undefined);
    });
    refresh_selection();
    if (name === 'world') fit_width();
    else map.getView().fit(disk_extent);
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
