(function () {
// Prevent double embedding
if (typeof(window.annotator) === 'undefined') {
    window.annotator = {};
} else {
    return;
}

var blocklist = (function() {
  'use strict';

  /* Parse the given URL and return an object with its different components.
  *
  * Any or all of the components returned may be undefined.
  * For example for the URL "http://twitter.com" port, path query and anchor
  * will be undefined.
  *
  */
  var parseUrl = function(url) {
    // Regular expression from Douglas Crockford's book
    // JavaScript: The Good Parts.
    var regex = /^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$/;
    var result = regex.exec(url);

    if (result) {
      return {
        scheme: result[1],
        host: result[3],
        port: result[4],
        path: result[5],
        query: result[6],
        anchor: result[7]
      };
    }

    return {
      scheme: undefined,
      host: undefined,
      port: undefined,
      path: undefined,
      query: undefined,
      anchor: undefined
    };
  };

  /* Return true if the given url is blocked by the given blocklist. */
  var isBlocked = function(url, blocklist) {
    url = url || '';

    // Match against the hostname only, so that a pattern like
    // "twitter.com" matches pages like "twitter.com/tag/foo".
    var hostname = parseUrl(url).host;

    if (hostname === undefined) {
      // This happens with things like chrome-devtools:// URLs where there's
      // no host.
      return false;
    }

    var regexSpecialChars = '^$.+?=|\/()[]{}'; //  '*' deliberately omitted.
    for (var pattern in blocklist) {
      if (blocklist.hasOwnProperty(pattern)) {
        // Escape regular expression special characters.
        for (var i = 0; i < regexSpecialChars.length; i++) {
          var c = regexSpecialChars.charAt(i);
          pattern = pattern.replace(c, '\\' + c);
        }

        // Turn * into .* to enable simple patterns like "*.google.com".
        pattern = pattern.replace('*', '.*');

        // Blocklist patterns should match from the start of the URL.
        // This means that "google.com" will _not_ match "mail.google.com",
        // for example. (But "*.google.com" will match it.)
        pattern = '^' + pattern;

        if (hostname.match(pattern)) {
          return true;
        }
      }
    }
    return false;
  };

  return {
    parseUrl: parseUrl,
    isBlocked: isBlocked
  };
})();

if (typeof(window.h) !== 'undefined') {
  // Looks like blocklist.js is being run by the Chrome extension, so add to
  // window.h like the rest of the Chrome extension libs do.
  window.h.blocklist = blocklist;
} else if (typeof(module) !== 'undefined') {
  // Looks like blocklist.js being run by the frontend tests, so export the
  // blocklist using browserify.
  module.exports = blocklist;
} else {
  // Looks like blocklist.js is being run by the bookmarklet, so we don't need
  // to export anything because it gets inlined into embed.js by Jinja2.
}

// Injects the hypothesis dependencies. These can be either js or css, the
// file extension is used to determine the loading method. This file is
// pre-processed in order to insert the wgxpath, url and inject scripts.
//
// Custom injectors can be provided to load the scripts into a different
// environment. Both script and stylesheet methods are provided with a url
// and a callback fn that expects either an error object or null as the only
// argument.
//
// For example a Chrome extension may look something like:
//
//   window.hypothesisInstall({
//     script: function (src, fn) {
//       chrome.tabs.executeScript(tab.id, {file: src}, fn);
//     },
//     stylesheet: function (href, fn) {
//       chrome.tabs.insertCSS(tab.id, {file: href}, fn);
//     }
//   });
window.hypothesisInstall = function (inject) {
  inject = inject || {};

  var resources = [];
  var injectStylesheet = inject.stylesheet || function injectStylesheet(href, fn) {
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = href;

    document.head.appendChild(link);
    fn(null);
  };

  var injectScript = inject.script || function injectScript(src, fn) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.onload = function () { fn(null) };
    script.onerror = function () { fn(new Error('Failed to load script: ' + src)) };
    script.src = src;

    document.head.appendChild(script);
  };

  
    // For certain blocklisted hostnames we bail out and don't inject
    // Hypothesis.
    var url = window.location.toString();
    if (blocklist.isBlocked(url, {})) {
      window.alert(
        "We're sorry, but Hypothesis doesn't work on " +
        window.location.hostname + " yet.");
      return;
    }
  

  if (!window.document.evaluate) {
    resources = resources.concat(['https://hypothes.is/assets/scripts/vendor/polyfills/wgxpath.install.min.js?bab1c82f']);
  }

  // https://github.com/Modernizr/Modernizr/blob/master/feature-detects/url/parser.js
  var url, urlWorks;
  try {
    // have to actually try use it, because Safari defines a dud constructor
    url = new URL('http://modernizr.com/');
    urlWorks = url.href === 'http://modernizr.com/';
  }
  catch (err) {
    urlWorks = false;
  }
  if (!urlWorks) {
    resources = resources.concat(['https://hypothes.is/assets/scripts/vendor/polyfills/url.min.js?de686538']);
  }

  if (typeof window.Annotator === 'undefined') {
    resources = resources.concat(['https://hypothes.is/assets/styles/hypothesis.min.css?0c35f899', 'https://hypothes.is/assets/scripts/hypothesis.min.js?d5f13ecc']);
  }

  (function next(err) {
    if (err) { throw err; }

    if (resources.length) {
      var url = resources.shift();
      var ext = url.split('?')[0].split('.').pop();
      var fn = (ext === 'css' ? injectStylesheet : injectScript);
      fn(url, next);
    }
  })();
}

var baseUrl = document.createElement('link');
baseUrl.rel = 'sidebar';
baseUrl.href = 'https://hypothes.is/app.html';
baseUrl.type = 'application/annotator+html';
document.head.appendChild(baseUrl);

window.hypothesisInstall();
})();