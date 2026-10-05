'use strict';
// Search organizations: first the ones already in EcoTaxa, then official ones from EDMO (https://edmo.seadatanet.org/).
// Suggestions show their EDMO and/or ROR codes, the ones not yet in EcoTaxa are marked with NEW_MARK.
import {
  fetchSettings
} from '../modules/utils.js';
const LOCAL_SEARCH_URL = '/api/organizations/search?name=';
const EDMO_SEARCH_URL = '/api/organizations/edmo_search?name=';
const NEW_MARK = '★';

// The code of a directory, e.g. 'edmo', in organization directories, e.g. "edmo:1278,ror:xxx", empty if none
function directoryCode(directories, directory) {
  const prefix = directory + ':';
  const entry = (directories || '').split(',').map(an_entry => an_entry.trim()).find(an_entry => an_entry.startsWith(prefix));
  return (entry) ? entry.substring(prefix.length) : '';
}

function codesLabel(edmo, ror) {
  return [(edmo !== '') ? 'EDMO ' + edmo : '', (ror !== '') ? 'ROR ' + ror : ''].filter(label => label !== '').join(' - ');
}

async function fetchJson(url) {
  const response = await fetch(url, fetchSettings());
  if (!response.ok) throw new Error(url + ' ' + response.status);
  return response.json();
}

// Organizations matching query: the ones in EcoTaxa then the ones from EDMO not yet in EcoTaxa, as {name, code, label}.
// token: the registration token, which gives an unlogged user access to EDMO search
export async function searchOrganizations(query, token = '') {
  // Suggestions are a help, the organization can be created without them, so one source failing does not hide the other
  const [local, edmo] = (await Promise.allSettled([
    fetchJson(LOCAL_SEARCH_URL + encodeURIComponent('%' + query + '%')),
    fetchJson(EDMO_SEARCH_URL + encodeURIComponent(query) + ((token) ? '&token=' + encodeURIComponent(token) : ''))
  ])).map(result => {
    if (result.status === 'fulfilled') return result.value;
    console.log('organization search', result.reason);
    return [];
  });
  const found = [];
  const localnames = new Set();
  const localcodes = new Set();
  local.forEach(organization => {
    const code = directoryCode(organization.directories, 'edmo');
    found.push({
      name: organization.name,
      code: code,
      label: codesLabel(code, directoryCode(organization.directories, 'ror'))
    });
    localnames.add(organization.name.toLowerCase());
    if (code !== '') localcodes.add(code);
  });
  edmo.forEach(organization => {
    const code = String(organization.code);
    if (localcodes.has(code) || localnames.has(organization.name.toLowerCase())) return;
    found.push({
      name: organization.name,
      code: code,
      label: NEW_MARK + ' ' + codesLabel(code, '')
    });
  });
  return found;
}
