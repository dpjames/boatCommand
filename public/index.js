const state = {
   location_interval : 1500, //how long to wait between location polls, ms
   spotlock_interval : 1500, //how long to wait between spotlock polls, ms
};
let locationstyle = new ol.style.Style({
   image : new ol.style.Circle({
      radius: 6,
      fill: new ol.style.Fill({color: 'blue'}),
      stroke: new ol.style.Stroke({
         color: "black", 
         width: 1,
      })
   })
});
let spotlockstyle = new ol.style.Style({
   image: new ol.style.Circle({
      radius: 10,
      fill: new ol.style.Fill({color: 'black'}),
      stroke: new ol.style.Stroke({
         color: "red", 
         width: 2,
      })
   })
});
function init(){
   state.baseLayer = new ol.layer.Tile({source : new ol.source.XYZ({minZoom : 10, maxZoom : 18})}); //empty shell filled in later
   state.baseLayer.getSource().setProperties({baseURL : "/maps/TYPE/{z}/{x}/{-y}.png"});
   state.locationFeature = new ol.Feature({geometry : new ol.geom.Point(ol.proj.fromLonLat([-120.472, 35.1941]))});
   state.spotlockFeature = new ol.Feature({geometry : new ol.geom.Point(ol.proj.fromLonLat([-120.472, 35.1941]))});
   state.locationLayer = new ol.layer.Vector({
      source : new ol.source.Vector({
         features : [state.locationFeature]
      }),
      style : f => f == state.locationFeature ? locationstyle : spotlockstyle,
   });
   state.map = new ol.Map({
      target : "map",
      layers: [
         state.baseLayer,
         state.locationLayer
      ],
      view: new ol.View({
         center: ol.proj.fromLonLat([-120.472, 35.1941]),
         zoom: 15,
      }),
      interactions : ol.interaction.defaults({altShiftDragRotate:false, pinchRotate:false}),
      controls : ol.control.defaults({rotate: false, zoom : false})
   });
   fillLocationsSelector();
   locationLoop();
}
function locationLoop(){
   const getLocation = () => {
      fetch("/location").then(v => v.json()).then(loc => {
         state.locationFeature.getGeometry().setCoordinates(ol.proj.fromLonLat(loc));
         setTimeout(locationLoop, state.location_interval);
      });
   }
   getLocation();
}
async function fillLocationsSelector(){
   const locations = await (fetch("/locations").then(v => v.json()));
   const locationsOptions = locations.map(loc => {
      return `<option value="${loc.center}">${loc.name}</option>`;
   });
   const locationsElement = document.getElementById("locations");
   locationsElement.innerHTML = locationsOptions.join("");
   const center = locationsElement.value.split(",")
   updateLayerType("topo");
   setCenter(center);
}
function setCenter(center){
   state.map.setView(new ol.View({
      center: ol.proj.fromLonLat(center),
      zoom: 15,
   }));
}
function updateLayerType(type){
   const source = state.baseLayer.getSource();
   const newurl = source.get("baseURL").replace("TYPE", type);
   source.setUrl(newurl);
}
function updateLayer(caller, op){
   switch(op){
      case "type":
         updateLayerType(caller.value);
         break;
      case "location":
         updateLayerLocation(caller.value);
         break;
      default:
         console.error("unknown layer change op", op);
   }
}
function updateLayerLocation(strParams){
   const center = strParams.split(",");
   setCenter(center);
}
function toggleControls(caller){
   const controls = document.getElementById("controls");
   controls.classList.toggle("hide");
   if(caller.dataset.state === "open"){
      caller.style.left = 0;
      caller.innerText = ">";
      caller.dataset.state = "closed";
   } else {
      caller.style.removeProperty("left");
      caller.innerText = "<";
      caller.dataset.state = "open";
   }
}
async function post(url, data){
   const response = await fetch(url, {
      method : "POST",
      mode : "cors",
      cache : "no-cache",
      headers : { "Content-Type" : "application/json"},
      body : JSON.stringify(data)
   });
   return response.json();
}
function spotLock(on){
   let alreadyLooping = state.spotLock;
   state.spotLock = on;
   post("/spotlock", {on : on}).then(resp => {;
      if(on && !alreadyLooping){
         spotLockLoop();
         addSpotLockPoint();
      }
   });
}
function spotLockLoop(){
   const spotLockOverlay = document.getElementById("spotLockOverlay");
   const looper = () => {
      fetch("/spotlock").then(v => v.json()).then(v => {
         spotLockOverlay.innerHTML = `Lock Location : ${v.lockedgps.map(v => v.toFixed(5))}, heading angle : ${v.heading[1].toFixed(2)}`;
         state.spotLock = v.running;
         if(state.spotLock) {
            setTimeout(looper, state.spotlock_interval);
         } else {
            spotLockOverlay.classList.add("hide");
            removeSpotLockPoint();
         }
      });
   }
   spotLockOverlay.classList.remove("hide");
   looper();
}

function addSpotLockPoint(){
   state.spotlockFeature.getGeometry().setCoordinates(state.locationFeature.getGeometry().getCoordinates());
   state.locationLayer.getSource().addFeature(state.spotlockFeature);
}
function removeSpotLockPoint(){
   state.locationLayer.getSource().removeFeature(state.spotlockFeature);
}



window.onload = init;
