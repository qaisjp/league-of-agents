# league-of-agents

We will provide a server with a simple API where you can control your fleet of cars and see the world status. In addition to this, we will also provide amazing mentors.

We don't care how you optimize the delivery of customers, it can be a simple if then, AI, machine learning, whatever. The challenge is for you to show off your skills in modern software development, prototyping, with a twist of shining creativity.

The solutions will be judged on creativity, impact, feasibility, novelty and cost efficiency.

This won Ericsson's "Greener city transport with 5G" challenge on the "Secure the Future" track,
at [Junction 2019](https://2019.hackjunction.com/).

## Agent

### Interface

```go
interface Agent {
    init(string team_name) -> Agent
    act(Observation ob) -> Action[]
}
```

### Input

**Observation**

```javascript
{
    "grid": Bool[][],
    "teams": Team[],
    "customers": Customer[],
    "ticks": Int,
}
```

**Team**

```javascript
{
    "id": String,
    "name": String,
    "cars": Car[],
    "score": Int,
}
```

**Car**

```javascript
{
    "id": String
    "position": Int[2],
    "capacity": Int,
    "available_capacity": Int,
    "customers": String[],
}
```

**Customer**

```javascript
{
    "id": String,
    "position": Int[2] | null,
    "destination": Int[2],
}
```

### Output

**Action**

```javascript
{
    "car": String,
    "direction": 0 | 1 | 2 | 3 | null
}
```


## API Library

```go
interface Agent {
    init(string base_url) -> API
    get_world() -> Observation
    move_car(string car_id, int direction, string token) -> void
    get_team_tokens() -> TeamToken[]
}
```

**TeamToken**

```javascript
{
    "id": Int,
    "name": String,
    "token": String,
}
```


## Visualiser

**Act**

```javascript
{
    "team": String,
    "actios": Action[],
}
```

**Step**

```javascript
{
    "state": Observation,
    "acts": Act[],
}
```
