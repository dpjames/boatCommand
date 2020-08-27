#!/bin/bash
#./cutToExtent.sh src dest extentfile
gdalwarp -of Gtiff -te $(cat $3) -t_srs "EPSG:4326" $1 $2
gdal2tiles.py -z 10-18 $2

