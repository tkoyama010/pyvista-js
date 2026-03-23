(function () {
  if (!document.querySelector('script[src*="model-viewer"]')) {
    var s = document.createElement("script");
    s.type = "module";
    s.src =
      "https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js";
    document.head.appendChild(s);
  }
  var gltfBytes = Uint8Array.from(atob(_gltfBase64), (c) => c.charCodeAt(0));
  var gltfBlob = new Blob([gltfBytes], { type: "model/gltf+json" });
  var gltfUrl = URL.createObjectURL(gltfBlob);
  var mv = document.createElement("model-viewer");
  mv.setAttribute("src", gltfUrl);
  mv.setAttribute("camera-controls", "");
  mv.style.cssText =
    "position:absolute;top:0;left:0;width:100%;height:100%;z-index:10;";
  mv.addEventListener("load", function () {
    URL.revokeObjectURL(gltfUrl);
  });
  container.appendChild(mv);
  // Unbind vtk.js interactor so model-viewer can receive pointer events
  if (typeof interactor !== "undefined" && interactor.unbindEvents) {
    interactor.unbindEvents();
  }
})();
