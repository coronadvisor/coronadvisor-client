require([
    "esri/Map",
    "esri/views/MapView",
    "esri/layers/FeatureLayer"
], function(Map, MapView, FeatureLayer) {
    var map = new Map({
        basemap: "streets-night-vector"
    });
    var lyr = new FeatureLayer({
        url:
            "https://services7.arcgis.com/htMxRutgdEUv2XFB/arcgis/rest/services/currentcases/FeatureServer",
        outFields: ["*"],
        popupTemplate: {
            title: "{Province_State}, {Country_Region}",
            content: "Confirmed: {Confirmed}"
        }
    });
    map.add(lyr);
    var view = new MapView({
        container: "viewDiv",
        map: map,
        center: [-20, 35],
        zoom: 2
    });
});
