class ReplayScene extends Phaser.Scene {
    constructor(config, applyNextStep) {
        console.debug("constructor", config);

        // this is some information for phaser about our scene
        const sceneConfig = {
            key: "replay-scene",
        };

        super(sceneConfig);

        this.config = config;
        this.applyNextStep = applyNextStep;

        this.viz = {
            lastUpdate: 0,
            state: "paused",
            city: null, // this will hold the latest data retrieved from server
        };

        this.map = null;
    }

    preload() {
        console.debug("preload");

        this.load.image('city-tiles', 'assets/elements.png');
    }

    create() {

    }

    updateSize(width) {
        console.debug("create");
        this.viz.width = width

        this.map = this.make.tilemap({
            width: width,
            height: width,
            tileWidth: TILE_WIDTH,
            tileHeight: TILE_WIDTH,
        });

        const tiles = this.map.addTilesetImage("city-tiles");

        const cityLayer = this.map.createBlankDynamicLayer("city-layer", tiles);

        const cityWidth = this.config.resolution.y;

        cityLayer.setDisplaySize(cityWidth, cityWidth);

        this.cameras.main.setScroll(
            -(this.config.resolution.x / 2) + (cityWidth / 2),
            0);
    }

    getCityGridTiles(grid) {
        const getCityGridTile = node => CITY_TILE_INDEXES[node ? "passable" : "impassable"];
        return grid.map(a => a.map(getCityGridTile));
    }

    getCustomerGridTiles(state, grid) {
        const customers = state.customers;
        const filtered = [];

        for (const team of state.teams) {
            for (const car of team.cars) {
                for (const customer of car.customers) {
                    filtered.push(customer);
                }
            }
        }
        // function getCustomerPosition(customer) {
        //     if (customer.status == "waiting") {
        //         return customer.origin;
        //     } else if (customer.status == "delivered")  {
        //         return customer.destination;
        //     } else {
        //         return;
        //     }
        // }

        for (const customer of customers) {
            if (filtered.includes(customer.id)) {
                continue;
            }
            const x = customer.position[0];
            const y = customer.position[1];
            grid[y][x] = 2;
        }

        // for (var key in customers) {
        //     if (getCustomerPosition(customers[key])) {
        //         grid[getCustomerPosition(customers[key])] = 2;
        //     }
        // }
        return grid;
    }

    getCarGridTiles(teams, grid) {
        for (const team of teams) {
            for (const car of team.cars) {
                const x = car.position[0]
                const y = car.position[1]
                grid[y][x] = 3 + Number.parseInt(team.id);
            }
        }
        return grid;
    }

    update(time, delta) {
        if (this.viz.state === "playing") {
            if ((time - this.viz.lastUpdate) > this.config.updateInterval) {
                this.viz.lastUpdate = time;
                this.applyNextStep()
            }
        }

        if (!this.step) {
            console.warn("not update — this.step does not exist")
            return
        }

        if (this.step.id === this.currentStepID) {
            console.log("not update — step has not changed")
            return
        }

        this.currentStepID = this.step.id

        if (this.step.state.grid.length !== this.viz.width) {
            this.updateSize(this.step.state.grid.length)
        }

        let gridTiles = this.getCityGridTiles(this.step.state.grid);
        gridTiles = this.getCustomerGridTiles(this.step.state, gridTiles)
        gridTiles = this.getCarGridTiles(this.step.state.teams, gridTiles)

        this.map.putTilesAt(gridTiles, 0, 0, false, "city-layer");
    }
}
