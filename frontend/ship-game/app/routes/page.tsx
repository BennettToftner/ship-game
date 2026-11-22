'use client';

import {setWorkerUrl, MapLayerMouseEvent} from 'maplibre-gl';
import Map from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

setWorkerUrl(new URL('maplibre-gl/dist/maplibre-gl-worker.mjs', import.meta.url).toString());

function clickHandler(e: MapLayerMouseEvent) {
    console.log(e);
}

export default function RoutesPage() {
    return (
        <Map
        initialViewState={{
            longitude: -122.4,
            latitude: 37.8,
            zoom: 14
        }}
        style={{width: 600, height: 400}}
        mapStyle="https://demotiles.maplibre.org/style.json"
        onClick={clickHandler}
        />
    );
}