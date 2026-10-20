# Idea: the world map

Status: idea, not a decision. For later, after the starter town.

## The idea

Above the city view, a world map: the player pulls out from a street to the town, from the town to its region, and from the region to a map of the world, and travels between towns and cities on it. A band tours; a family emigrates; a detective follows a lead to another city; a venture opens a branch. Each town or city is its own setting pack, all in one world on the same engine.

## What it would be

- **A third scale of view.** The scene view (a room, a gig), the city view (the live town from above), and the world map (an illustrated chart showing only what the player knows: towns visited, routes travelled, people met there).
- **Travel as facts.** Routes (a ferry, a railway, a road, a flight) carry time and cost, from the setting's era: a 1989 ferry to Bergen takes hours, a flight to London a day of the player's month. Travel is part of the story, not a loading screen.
- **People who move.** The engine's people live in more than one place: a band tours and comes home changed, someone leaves for Oslo and returns twenty years later.
- **One look at every scale.** The map is painted in the same style, as a chart or an atlas of its era, never a generic game map.

## What the starter town keeps open now

- **Its place on the globe.** The town has a latitude, longitude and time zone, and its light is computed from them: Stavanger at 59°N has short December days and light June nights; London at 51°N and New York at 41°N each get their own day and year. Every city's light becomes a fact of where it is.
- **A region that exists around it** (`docs/town-plan.md`, Expansion), so the camera can pull out past the town's edge to land, coast and neighbouring places.
- **Routes out of town as places:** the ferry quay, the station, the airport, the motorway. They become the doors to the world map.
- **Setting packs that can sit side by side:** nothing in a pack assumes it is the only place in the world.

## Open questions

- Does the engine hold several places in one world, and how do its people move between them? (`docs/engine-requests.md`, Later)
- How much of a distant city is simulated while the player is elsewhere?
- What does travel cost the player in time, and what happens at home meanwhile?
