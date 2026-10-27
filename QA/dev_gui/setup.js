// alert-box.js fetches the translations at import time (top-level await):
// answer it locally so modules importing alert-box load without the Flask app.
const realFetch = globalThis.fetch;
globalThis.fetch = (input, init) => {
  const url = (typeof input === 'string') ? input : input.url;
  if (url.includes('/gui/i18n')) {
    return Promise.resolve(new Response('{}', {
      headers: { 'Content-Type': 'application/json' },
    }));
  }
  return realFetch(input, init);
};
