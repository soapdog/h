(function () {
  /*
   * I had no destroy.js so I created one. It looks for the DOMElements
   * added by embed.js and destroy them all!!!
   */


   // REMOVING THE EASY STUFF
   var selectors = [
     "div.annotator-adder",
     "div.annotator-frame",
     "div.annotator-notice",
     'script[src$="/hypothesis/data/embed.js"]',
     'script[src$="/hypothesis/data/destroy.js"]',
     'link[href="https://hypothes.is/app.html"]',
     'link[href^="https://hypothes.is/assets/styles/hypothesis.min.css"]',
     'script[src^="https://hypothes.is/assets/scripts/hypothesis.min.js"]'
   ];

   selectors.forEach(function(selector) {
     console.log("removing " + selector);
     var el = document.querySelector(selector);

     if (el) {
       el.remove();
     }

   });

   // Needs to remove all those event handlers in HTML and BODY.
   // TODO: The hypothesis script adds lot of event handlers. They need to
   // be removed but I don't have references to them. Maybe it is easier to
   // reload the tab instead (uglier but it works).

    var bodyEventListenersToBeRemoved = [
        "click",
        "mousedown",
        "mouseup",
        "setVisibleHighlights",
        "beforeAnnotationsCreated",
        "annotationCreated",
        "annotationUpdated",
        "annotationDeleted",
        "annotationsLoaded",
        "resize",
        "scroll",
        "hightlightsCreated",
        "highlightRemoved",
        "panelReady"
    ];

    bodyEventListenersToBeRemoved.forEach(function(eventName){
        // TODO: Find a way of removing these events.
        //document.body.removeEventListener(eventName);
    });

    var htmlEventListenersToBeRemoved = [
        "message",
        "scroll",
        "resize",
        "mouseup",
        "mousemove",
        "docPageScrolling"
    ];

    htmlEventListenersToBeRemoved.forEach(function(eventName){
        // TODO: Find a way of removing these events.

        //document.removeEventListener(eventName);
    });

   // REMOVING ANNOTATOR GLOBAL
   delete window.annotator;

})();
