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

const viz = {}

const clearUI = () => {
    document.querySelector("#status").textContent = "";
}

const onSwitchLive = e => {
    clearUI();
    if (e.target.checked) {
        alert("going to live")
        viz.scenes.remove("replay-scene")
        viz.scenes.add("live-scene", new LiveScene(visualsConfig))
        viz.scenes.run("live-scene")
    } else {
        alert("leaving live")
        viz.scenes.remove("live-scene")
        viz.scenes.add("replay-scene", new ReplayScene(visualsConfig))
        viz.scenes.run("replay-scene")
    }
}

const onChooseFileDrop = async event => {
    let files = event.dataTransfer.files;

    if (files.length !== 1) {
        alert("Expected exactly 1 file")
        return
    }

    const file = files[0]
    if (file.type !== "application/json") {
        alert("File must be application/json")
        return
    }

    const code = document.querySelector("#codebox")
    code.textContent = await file.text();
}

const eventStopAndPrevent = event => {
    event.stopPropagation()
    event.preventDefault()
}

window.addEventListener("load", () => {
    document.querySelector("#live").addEventListener("change", onSwitchLive)

    const code = document.querySelector("#codebox")

    code.addEventListener("dragover", eventStopAndPrevent)
    code.addEventListener("dragenter", eventStopAndPrevent)
    code.addEventListener("drop", eventStopAndPrevent)
    code.addEventListener("drop", onChooseFileDrop)


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

    viz.game = new Phaser.Game(phaserConfig);
    viz.scenes = new Phaser.Scenes.SceneManager(viz.game);
})
