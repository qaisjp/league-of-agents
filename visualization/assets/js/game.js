'use strict';

const visualsConfig = {
// @serverAddr: Address of the server to connect to, eg. 'http://localhost:8000'
//              If empty, uses the same server the visualization is hosted on.
    serverAddr: "http://localhost:8080",
    updateInterval: 50, // ms
    resolution: {
        x: 1080,
        y: 1080,
    },
};

const TILE_WIDTH = 30;

// maps passability to the tiles in dirt.png
const CITY_TILE_INDEXES = {
    passable: 0,
    impassable: 1,
};

window.addEventListener("load", () => {
    const phaserConfig = {
        type: Phaser.AUTO,
        width: visualsConfig.resolution.x,
        height: visualsConfig.resolution.y,
        physics: {
            default: 'arcade',
            arcade: {
                debug: true     // TODO
            }
        },
        scene: [new LiveScene(visualsConfig)],
        parent: document.querySelector("#right"),
    };

    const game = new Phaser.Game(phaserConfig);
})
