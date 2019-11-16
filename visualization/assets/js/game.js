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
    scene: null,
    data: null
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

    const newScene = viz.live ? new LiveScene(visualsConfig) : new ReplayScene(visualsConfig, applyNextStep)
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

    viz.el.frameInput.value = id
    viz.el.slider.value = id

    viz.scene.step = step
}

const setPaused = state => {
    if (state === null) {
        state = viz.scene.viz.state === "playing"
    }

    viz.scene.viz.state = state ? "paused" : "playing"
    viz.el.playpause.textContent = state ? "play" : "pause"
}

const apply = () => {
    const obj = JSON.parse(viz.el.code.value);
    viz.data = obj;

    const maxVal = obj.steps.length - 1

    viz.el.slider.setAttribute("max", maxVal)
    viz.el.slider.value = "0"

    viz.el.frameInput.setAttribute("max", maxVal)
    viz.el.frameInput.value = "0"

    setPaused(true)
    applyStep(0)
}

const applyNextStep = () => {
    console.log("applying next step");
    let next = viz.scene.step.id + 1
    if (next >= viz.data.steps.length) {
        next = 0
    }
    applyStep(next)
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

const togglePlayPause = () => {
    setPaused(null)
}

const onUpdateInterval = e => {
    if (e.target.textContent.length > 0) {
        const direction = (e.target.textContent === "speed up") ? -1 : 1
        visualsConfig.updateInterval += 50 * direction
        if (visualsConfig.updateInterval <= 0) {
            visualsConfig.updateInterval = 50
        }
        viz.el.gamespeed.value = visualsConfig.updateInterval
    } else {
        visualsConfig.updateInterval = e.target.value
    }
}

window.addEventListener("load", () => {
    viz.el = {}
    viz.el.teams = document.querySelector("#teams")
    viz.el.frameInput = document.querySelector("#frame-input")

    viz.el.playpause = document.querySelector("#playpause")
    viz.el.playpause.addEventListener("click", togglePlayPause)

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

    viz.el.gamespeed = document.querySelector("#gamespeed")
    viz.el.gamespeed.value = visualsConfig.updateInterval
    viz.el.gamespeed.addEventListener("change", onUpdateInterval)

    viz.el.gamespeeddown = document.querySelector("#gamespeeddown")
    viz.el.gamespeeddown.addEventListener("click", onUpdateInterval)
    viz.el.gamespeedup = document.querySelector("#gamespeedup")
    viz.el.gamespeedup.addEventListener("click", onUpdateInterval)

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