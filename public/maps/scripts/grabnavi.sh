#!/bin/bash


#there is a origin block on these urls :( but what you can do is twofold:
#1 goto the navionics web viewer and run this code in the console: 
#
#
#Array.from(document.querySelectorAll("*")).forEach(e => {
#let l = getEventListeners(e).contextmenu;
#if(l){
#   l.forEach(item => {
#   console.log("yes");
#   e.removeEventListener("contextmenu", item.listener)
#});
#}     
#});
#then set the window size to huge, browse to your desired lake, right click, download map, use qgis to geolocate the map, then tile it.

#OR rewrite this script to write js for you that runs from bassresoure.com to download all the tiles. I like the above option more.
z=16
basedir=$(pwd)
cd ../topo/$z
rm -rf $z
mkdir $basedir/$z
for x in *
do
   mkdir $basedir/$z/$x
   cd $x
      for y in *
      do
         #y is actually 2^z - 1 - y
         newy=$(awk "BEGIN{print 2^$z - 1 - $y}")
         echo $y
         echo $newy
         echo "$z/$x/$newy"
         #get an apikey from here: https://www.bassresource.com/maps/fishing-spots-maps.html
         url="https://tile3.navionics.com/tile/$z/$x/$newy?LAYERS=config_1_0.00_0&TRANSPARENT=FALSE&UGC=TRUE&theme=0&navtoken=eyJrZXkiOiJOYXZpb25pY3Nfd2ViYXBpXzAyOTI0Iiwia2V5RG9tYWluIjoid3d3LmJhc3NyZXNvdXJjZS5jb20iLCJyZWZlcmVyIjoid3d3LmJhc3NyZXNvdXJjZS5jb20iLCJyYW5kb20iOjE1OTg1MTczMTIyNzR9"
         echo "$url"
         #wget -O "$basedir/$z/$x/$newy" $url
      done
   cd ..
done

