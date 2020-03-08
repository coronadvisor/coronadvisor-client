require([
    "esri/Map",
    "esri/views/MapView",
    "esri/layers/FeatureLayer"
], function(Map, MapView, FeatureLayer) {
    var map = new Map({
        basemap: "streets-night-vector"
    });

    console.log(window.queryDateStart);
    console.log(window.queryDateEnd);

    var predictedCase = new FeatureLayer({
        url:
            "https://services7.arcgis.com/htMxRutgdEUv2XFB/arcgis/rest/services/prediction_final/FeatureServer",
        outFields: ["*"],
        popupTemplate: {
            title: "{Countries}",
            content: `
            Predicted Confirmed: {Confirmed}<br>

            Predicted Recovered: {Recovered}<br>
            
            Predicted Death: {Deaths}<br>
            `
        },
        timeInfo: {
            interval: {
                // specify time interval for
                unit: "days",
                value: 1
            }
        },
        definitionExpression: `Date BETWEEN timestamp '${window.queryDateStart} 07:00:00' AND timestamp '${window.queryDateEnd} 06:59:59'`,
        useViewTime: false
    });

    console.log(predictedCase.timeInfo);
    console.log(predictedCase.timeExtent);
    map.add(predictedCase);
    var view = new MapView({
        container: "viewDiv",
        map: map,
        center: [-20, 35],
        zoom: 2
    }); // create a new TimeSlider widget
});
