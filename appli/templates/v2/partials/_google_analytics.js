{ % -
  if g.google_analytics_id and g.cookieGAOK == 'Y' - %
} { % -set gkey = 'G-FQGS0MYN66' - %
}
<!-- Google tag (gtag.js) -->
<
script async src = "https://www.googletagmanager.com/gtag/js?id=G-FQGS0MYN66" > < /script> <
  script >
  window.dataLayer = window.dataLayer || [];

function gtag() {
  dataLayer.push(arguments);
}
gtag('js', new Date());
gtag('config', 'G-FQGS0MYN66'); <
/script>
<!-- Google Tag Manager -->
<
script nonce = '{SERVER-GENERATED-NONCE}' > (function(w, d, s, l, i) {
  w[l] = w[l] || [];
  w[l].push({
    'gtm.start': new Date().getTime(),
    event: 'gtm.js'
  });
  var f = d.getElementsByTagName(s)[0],
    j = d.createElement(s),
    dl = l != 'dataLayer' ? '&l=' + l : '';
  j.async = true;
  j.src =
    'https://www.googletagmanager.com/gtm.js?id=' + i + dl;
  var n = d.querySelector('[nonce]');
  n && j.setAttribute('nonce', n.nonce || n.getAttribute('nonce'));
  f.parentNode.insertBefore(j, f);
})(window, document, 'script', 'dataLayer', '{{gkey}}'); < /script>
<!-- End Google Tag Manager -->
{ % -endif - %
}