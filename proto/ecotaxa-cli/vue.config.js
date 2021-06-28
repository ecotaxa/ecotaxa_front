// vue.config.js

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */
 module.exports = {
  // options...
  publicPath: process.env.NODE_ENV === "production" ? "/front/" : "/",
  devServer: {
    // https://webpack.js.org/configuration/dev-server/#devserverhistoryapifallback
    historyApiFallback: true,
    proxy: {
      "/api": {
        target: "https://ecotaxa.obs-vlfr.fr/",
        // Uncomment below for using local python server which does proxying on /api to local docker
        //target: "http://localhost:5001/",
        // Uncomment below for using local docker
        //target: "http://localhost:8000/",
        ws: true,
        changeOrigin: true,
        onProxyReq: (proxyReq, req) => {
          // Remove session cookies which are the session b/w client and dev web server, thus useless to prod' site
          // TODO: A real login via API in such case
          if ("cookie" in req.headers && proxyReq.host !== "localhost") {
            proxyReq.removeHeader("cookie");
          }
          // On Chrome, get your EcoTaxa session cookie, by :
          // 1) Use EcoTaxa
          // 2) On up-right corner, click vertical ...
          // 3) Go to More tools/Developer tools/Application/Storage/Cookies/<EcoTaxa site>/session
          // To make it work with a "session cookie", uncomment the 2 following lines :
          // const session_cookie = "PUT HERE THE SESSION COOKIE... LONG STRING";
          // proxyReq.setHeader("Authorization", "Bearer " + session_cookie);          
        },
      },
    },
  },
};
