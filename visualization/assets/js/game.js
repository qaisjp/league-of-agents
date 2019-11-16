'use strict';

const visualsConfig = {
// @serverAddr: Address of the server to connect to, eg. 'http://localhost:8000'
//              If empty, uses the same server the visualization is hosted on.
    serverAddr: "http://localhost:8080",
    updateInterval: 500, // ms
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

const viz = {
    live: true,
    scene: null
}

const clearUI = () => {
    document.querySelector("#status").textContent = ""
    clearStepUI()
}

const clearStepUI = () => {
    document.querySelector("#teams").innerHTML = ""
}

const onSwitchLive = e => {
    clearUI();

    viz.live = e.target.checked

    const newScene = viz.live ? new LiveScene(visualsConfig) : new ReplayScene(visualsConfig)
    loadGame(newScene)
}

const applyStep = id => {
    clearStepUI()

    if (viz.live) {
        alert("not applying step because live")
        return
    }

    if (!Number.isFinite(id)) {
        alert("step ID must be a (finite) number")
        return
    }

    if (viz.data == null) {
        alert("replay data not loaded yet")
        return
    }

    if (id >= viz.data.steps.length) {
        alert("step " + id + " does not exist. must be <" + viz.data.steps.length)
        return
    }

    const step = viz.data.steps[id]
    step.id = id
    const teamsEl = viz.el.teams
    for (const team of step.state.teams) {
        const opt = document.createElement("option");
        opt.text = team.name;
        teamsEl.add(opt)
    }

    viz.scene.step = step
}

const apply = () => {
    const obj = JSON.parse(viz.el.code.value);
    viz.data = obj;

    const maxVal = obj.steps.length - 1

    viz.el.slider.setAttribute("max", maxVal)
    viz.el.slider.value = "0"

    viz.el.frameInput.setAttribute("max", maxVal)
    viz.el.frameInput.value = "0"

    applyStep(0)
}

const onChooseFileDrop = async event => {
    event.stopPropagation()
    event.preventDefault()

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

    viz.el.code.value = await file.text();

    apply()
}

const eventStopAndPrevent = event => {
    event.stopPropagation()
    event.preventDefault()
}

const onSliderChange = event => {
    applyStep(Number.parseInt(event.target.value))
}

const onSliderInput = event => {
    viz.el.frameInput.value = event.target.value
}

window.addEventListener("load", () => {
    viz.el = {}
    viz.el.teams = document.querySelector("#teams")
    viz.el.frameInput = document.querySelector("#frame-input")

    viz.el.slider = document.querySelector("#frame-range")
    viz.el.slider.addEventListener("input", onSliderInput)
    viz.el.slider.addEventListener("change", onSliderChange)

    viz.el.live = document.querySelector("#live")
    viz.el.live.addEventListener("change", onSwitchLive)

    viz.el.code = document.querySelector("#codebox")
    viz.el.code.addEventListener("dragover", eventStopAndPrevent)
    viz.el.code.addEventListener("dragenter", eventStopAndPrevent)
    viz.el.code.addEventListener("drop", onChooseFileDrop)

    viz.el.reload = document.querySelector("#btn-reload")
    viz.el.reload.addEventListener("click", apply)

    loadGame(new LiveScene(visualsConfig))
})

const loadGame = scene => {
    if (viz.game != null) {
        viz.game.destroy(true)
        viz.game = null;
        setTimeout(loadGame.bind(null, scene))
        return
    }


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
        scene: [scene],
        parent: document.querySelector("#right"),
    };

    viz.game = new Phaser.Game(phaserConfig);
    viz.scene = scene
}