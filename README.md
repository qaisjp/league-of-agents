# league-of-agents

We will provide a server with a simple API where you can control your fleet of cars and see the world status. In addition to this, we will also provide amazing mentors.

We don't care how you optimize the delivery of customers, it can be a simple if then, AI, machine learning, whatever. The challenge is for you to show off your skills in modern software development, prototyping, with a twist of shining creativity.

The solutions will be judged on creativity, impact, feasibility, novelty and cost efficiency.

The winning team will receive €2000.

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
    "map": Bool[][],
    "teams": Team[],
    "customers": Customer[],
}
```

**Team**

```javascript
{
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
    "availableCapacity": Int,
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
    getWorld() -> Observation
    moveCar(string team_name, string car_id, int direction) -> void
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
