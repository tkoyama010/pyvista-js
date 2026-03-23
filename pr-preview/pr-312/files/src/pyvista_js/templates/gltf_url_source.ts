(function () {
  if (!document.querySelector('script[src*="model-viewer"]')) {
    var s = document.createElement("script");
    s.type = "module";
    s.src =
      "https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js";
    document.head.appendChild(s);
  }
  var mv = document.createElement("model-viewer");
  mv.setAttribute("src", _gltfUrl);
  mv.setAttribute("camera-controls", "");
  mv.setAttribute("auto-rotate", "");
  mv.style.cssText =
    "position:absolute;top:0;left:0;width:100%;height:100%;z-index:10;";
  container.appendChild(mv);
  // Unbind vtk.js interactor so model-viewer can receive pointer events
  if (typeof interactor !== "undefined" && interactor.unbindEvents) {
    interactor.unbindEvents();
  }
})();
