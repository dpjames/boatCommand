const state = {
   location_interval : 500, //how long to wait between location polls, ms
   spotlock_interval : 500, //how long to wait between spotlock polls, ms
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
         new ol.layer.Tile({source: new ol.source.OSM()}),
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
   const locationsHTML = locations.map(loc => {
      return `
         <div class="locationBox" onclick="setCenter(${JSON.stringify(loc.center)})">
            <div>${loc.name}</div>
            <img src="${loc.thumbnail}"></img>
         </div>
         `;
         
         //<option value="${loc.center}">${loc.name}</option>`;
   });
   const locationsElement = document.getElementById("locations");
   locationsElement.innerHTML = locationsHTML.join("");
   const center = locations[0].center;
   updateLayerType("topo");
   setCenter(center);
}
function setCenter(center){
   state.map.setView(new ol.View({
      center: ol.proj.fromLonLat(center),
      zoom: 15,
   }));
}
function updateLayerType(type, caller){
   if(caller){
      caller.closest(".tabs").querySelector(".active").classList.remove("active");
      caller.classList.add("active");
   }
   const source = state.baseLayer.getSource();
   const newurl = source.get("baseURL").replace("TYPE", type);
   source.setUrl(newurl);
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
function toggleSensors(caller){
   const controls = document.getElementById("sensors");
   controls.classList.toggle("hide");
   if(caller.dataset.state === "open"){
      caller.innerText = "^";
      caller.dataset.state = "closed";
   } else {
      caller.innerText = "v";
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
   state.spotlockpoints = [[],[]];
   const looper = () => {
      fetch("/spotlock").then(v => v.json()).then(v => {
         state.spotlockpoints[0].push(v.heading[0]);
         state.spotlockpoints[1].push(v.heading[1]);
         updateGraph("spotlockmaggraph", state.spotlockpoints[0], [0,.0004]);
         updateGraph("spotlockdirgraph", state.spotlockpoints[1], [-180,180]);
         state.spotLock = v.running;
         if(state.spotLock) {
            setTimeout(looper, state.spotlock_interval);
         } else {
            removeSpotLockPoint();
         }
      });
   }
   looper();
}
function updateGraph(id, arr, range){
   const canvas = document.getElementById(id);
   const w = canvas.width;
   const h = canvas.height;
   const pen = canvas.getContext("2d");
   const positive_delta = Math.abs(Math.min(0, range[0]));
   const min = range[0] + positive_delta; 
   const max = range[1] + positive_delta;
   arr = arr.slice(Math.max(arr.length - w, 0));
   pen.clearRect(0,0,w,h);
   for(let x = 0; x < arr.length; x++){
      const v = arr[x] + positive_delta;
      const y = h * ((v - min) / max);
      pen.fillRect(x,h - y,1,y);
   }
}
function addSpotLockPoint(){
   state.spotlockFeature.getGeometry().setCoordinates(state.locationFeature.getGeometry().getCoordinates());
   state.locationLayer.getSource().addFeature(state.spotlockFeature);
}
function removeSpotLockPoint(){
   state.locationLayer.getSource().removeFeature(state.spotlockFeature);
}
function toggleSettings(caller){
   caller.classList.toggle("exitButton");
   caller.classList.toggle("settingsButton");
   document.querySelector('#settings').classList.toggle('hide');
}
function findMe(){
   state.map.getView().setCenter(state.locationFeature.getGeometry().getCoordinates())
}
window.onload = init;

