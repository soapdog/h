const self = require("sdk/self");
const data = self.data;
const tabs = require("sdk/tabs");
const { ToggleButton } = require("sdk/ui/button/toggle");
var btnConfig = {};
var btn;
var ss = require("sdk/simple-storage");
if (!ss.storage.pages) {
  // This array will keep track on which pages the
  // add-on should activate.
  ss.storage.pages = [];
}

console.log("storage: ", ss.storage.pages);

// NOTE: The 18 and 36 icons are actually 16x16 and 32x32 respectively as
// FireFox will downscale 18x18 icons. I can't find any documentation on
// on why this happens or how to prevent this.
var icons = {
  'sleeping': {
    "18": data.url('images/toolbar-inactive.png'),
    "32": data.url('images/menu-item.png'),
    "36": data.url('images/toolbar-inactive@2x.png'),
    "64": data.url('images/menu-item@2x.png')
  },
  // for all occasionas
  'active': {
    "18": data.url('images/toolbar-active.png'),
    "32": data.url('images/menu-item.png'),
    "36": data.url('images/toolbar-active@2x.png'),
    "64": data.url('images/menu-item@2x.png')
  }
};

function enable(tab) {
  tab.attach({
    contentScript: [
      'var s = document.createElement("script");',
      's.setAttribute("src", "' + data.url('embed.js') + '");',
      'document.body.appendChild(s);'
    ]
  });
}

function disable(tab) {

   //TODO: The destroy.js script is not able to remove all scripts
   //injected by hipothesis, reloading the tab solves that.

   tab.attach({
     contentScript: [
       'var s = document.createElement("script");',
       's.setAttribute("src", "' + data.url('destroy.js') + '");',
       'document.body.appendChild(s);'
     ]
   });

  //tab.reload();

}

function activate(btn, tab) {
  btn.state(tab, {
    checked: true,
    label: 'Annotating',
    icon: icons.active
  });

  // Keep track of what pages we should activate the add-on
  if (ss.storage.pages.indexOf(tab.url) !== -1) {
    ss.storage.pages.push(tab.url);
  }
  console.log("activate storage: ", ss.storage.pages);

}

function deactivate(btn, tab) {
  btn.state(tab, {
    checked: false,
    label: 'Annotate',
    icon: icons.sleeping
  });

  // Remove page from the tracked page array
  ss.storage.pages = ss.storage.pages.filter(function(e){return e!==tab.url});

  console.log("deactivate storage: ", ss.storage.pages);


}

btnConfig = {
  id: "hypothesis",
  label: "Annotate",
  icon: icons.sleeping,
  onClick: function onButtonClick(state) {
    // delete the window-wide state default
    this.state('window', null);
    // but turn it back on for this tab
    if (this.state(tabs.activeTab).checked !== true) {
      activate(btn, tabs.activeTab);
      enable(tabs.activeTab);
    } else {
      deactivate(btn, tabs.activeTab);
      disable(tabs.activeTab);
    }
  }
};

if (typeof ToggleButton === 'undefined') {
  btn = require("sdk/widget").Widget(btnConfig);
} else {
  btn = ToggleButton(btnConfig);
}

tabs.on('pageshow', function onPageShow(tab) {
  if (btn.state(tab).checked) {
    enable(tab);
  } else {
    disable(tab);
  }

  // check if it is a tracked page
  if (ss.storage.pages.indexOf(tab.url) !== -1) {
    console.log("activating because ss");
    console.log(ss.storage.pages);
    enable(tab);
  }

});

tabs.on('open', function onTabOpen(tab) {
  // h is off by default on new tabs
  deactivate(btn, tab);
});

exports.main = function main(options, callbacks) {
  if (options.loadReason === 'install') {
    tabs.open({
      url: 'https://hypothes.is/welcome',
      onReady: function onTabReady(tab) {
        activate(btn, tab);
      }
    });
  }
};

exports.onUnload = function onUnload(reason) {
  if (reason === 'uninstall' || reason === 'disable') {
    [].forEach.call(tabs, disable);
  }
};
