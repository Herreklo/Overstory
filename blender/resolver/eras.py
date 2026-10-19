"""Era shelves for the first region: the North Atlantic timber harbour town.

Each era lists what was built and installed in its years: proportions, roofs,
windows, doors, shopfronts, ornament and colours. A part is always taken from the
shelf of the year it was installed. Lengths are millimetres, angles tenths of a
degree, chances per mille. Values are provisional until look tests settle them.
Sources: Stavanger's wooden-town guidance and the research docs in the Project.
"""

from hashing import weighted

ERAS = {
    "classical": dict(
        years=(1790, 1869),
        storey=2850, pitch=(380, 420), eave=300, gable=200, kick=0,
        roof=[("gable", 70), ("mansard", 30)],
        storeys=[(1500, 50), (2000, 50)],
        plinth=(400, 700),
        window="small_panes", door="panel_fanlight", shopfront="shop_1900",
        ornament=dict(fret=0, brackets=0, finial=0, pediment=0, cornice=900, belt=600, pilasters=800, crossing=0),
        additions=dict(ark=100, bislag=350, veranda=50, bay=0, dormer=250),
        symmetric=900,
        walls=[("wall_white", 40), ("wall_cream", 25), ("wall_oxred", 15), ("wall_grey", 20)],
        trims=[("trim_white", 70), ("door_green", 15), ("wall_ochre", 15)],
        roofs=[("roof_red", 80), ("roof_red_dark", 20)],
        doors=[("door_green", 40), ("door_brown", 30), ("door_blue", 30)],
        care=900,
    ),
    "chalet": dict(
        years=(1865, 1909),
        storey=3000, pitch=(450, 520), eave=650, gable=500, kick=600,
        roof=[("gable", 100)],
        storeys=[(1500, 30), (2000, 45), (2500, 25)],
        plinth=(600, 1100),
        window="cross_t", door="chalet_glass", shopfront="shop_1900",
        ornament=dict(fret=850, brackets=900, finial=700, pediment=900, cornice=0, belt=500, pilasters=0, crossing=700),
        additions=dict(ark=550, bislag=500, veranda=450, bay=350, dormer=400),
        symmetric=250,
        walls=[("wall_ochre", 25), ("wall_cream", 25), ("wall_white", 30), ("wall_yellow", 10), ("wall_green", 10)],
        trims=[("trim_white", 50), ("door_green", 20), ("door_brown", 20), ("trim_cream", 10)],
        roofs=[("roof_slate", 40), ("roof_black", 30), ("roof_red", 30)],
        doors=[("door_green", 30), ("door_brown", 40), ("door_red", 15), ("door_blue", 15)],
        care=800,
    ),
    "jugend": dict(
        years=(1905, 1925),
        storey=3000, pitch=(480, 550), eave=350, gable=250, kick=300,
        roof=[("gable", 50), ("mansard", 50)],
        storeys=[(2000, 60), (2500, 40)],
        plinth=(500, 900),
        window="cross_arch", door="chalet_glass", shopfront="shop_1900",
        ornament=dict(fret=0, brackets=500, finial=300, pediment=0, cornice=700, belt=400, pilasters=300, crossing=0),
        additions=dict(ark=450, bislag=300, veranda=400, bay=450, dormer=500),
        symmetric=300,
        walls=[("wall_white", 70), ("wall_cream", 20), ("wall_grey", 10)],
        trims=[("trim_white", 85), ("trim_cream", 15)],
        roofs=[("roof_slate", 50), ("roof_red_dark", 50)],
        doors=[("door_brown", 50), ("door_green", 30), ("door_blue", 20)],
        care=800,
    ),
    "functionalist": dict(
        years=(1930, 1950),
        storey=2700, pitch=(180, 240), eave=250, gable=150, kick=0,
        roof=[("gable", 60), ("flat", 40)],
        storeys=[(1000, 20), (2000, 80)],
        plinth=(300, 500),
        window="band", door="funkis_canopy", shopfront="shop_1930",
        ornament=dict(fret=0, brackets=0, finial=0, pediment=0, cornice=0, belt=0, pilasters=0, crossing=0),
        additions=dict(ark=0, bislag=0, veranda=100, bay=150, dormer=0),
        symmetric=100,
        walls=[("wall_oxred", 25), ("wall_ochre", 25), ("wall_green", 20), ("wall_yellow", 15), ("wall_blue", 15)],
        trims=[("trim_white", 100)],
        roofs=[("roof_black", 100)],
        doors=[("trim_dark", 60), ("door_blue", 40)],
        care=500,
    ),
    "postwar": dict(
        years=(1945, 1965),
        storey=2600, pitch=(220, 300), eave=350, gable=250, kick=0,
        roof=[("gable", 100)],
        storeys=[(1000, 40), (1500, 30), (2000, 30)],
        plinth=(300, 600),
        window="picture", door="teak_strip", shopfront="shop_1960",
        ornament=dict(fret=0, brackets=0, finial=0, pediment=0, cornice=0, belt=0, pilasters=0, crossing=0),
        additions=dict(ark=0, bislag=200, veranda=0, bay=100, dormer=150),
        symmetric=200,
        walls=[("wall_yellow", 20), ("wall_green", 20), ("wall_blue", 20), ("wall_grey", 20), ("wall_white", 20)],
        trims=[("trim_white", 100)],
        roofs=[("roof_black", 60), ("roof_slate", 40)],
        doors=[("wood", 60), ("door_red", 20), ("door_blue", 20)],
        care=400,
    ),
    "seventies": dict(
        years=(1965, 1980),
        storey=2500, pitch=(200, 260), eave=500, gable=400, kick=0,
        roof=[("gable", 100)],
        storeys=[(1000, 40), (2000, 60)],
        plinth=(200, 400),
        window="casement", door="teak_strip", shopfront="shop_1960",
        ornament=dict(fret=0, brackets=0, finial=0, pediment=0, cornice=0, belt=0, pilasters=0, crossing=0),
        additions=dict(ark=0, bislag=0, veranda=0, bay=0, dormer=0),
        symmetric=100, cladding="vertical",
        walls=[("wall_brown", 70), ("wall_oxred", 30)],
        trims=[("trim_white", 50), ("trim_dark", 50)],
        roofs=[("roof_black", 70), ("roof_slate", 30)],
        doors=[("wood", 100)],
        care=200,
    ),
    "eighties": dict(
        years=(1980, 1995),
        storey=2500, pitch=(250, 350), eave=450, gable=350, kick=0,
        roof=[("gable", 100)],
        storeys=[(1500, 50), (2000, 50)],
        plinth=(200, 400),
        window="stick_bars", door="eighties", shopfront="shop_1980",
        ornament=dict(fret=0, brackets=0, finial=0, pediment=0, cornice=0, belt=0, pilasters=0, crossing=0),
        additions=dict(ark=150, bislag=100, veranda=0, bay=100, dormer=200),
        symmetric=200,
        walls=[("wall_cream", 30), ("wall_blue", 25), ("wall_green", 25), ("wall_yellow", 20)],
        trims=[("trim_white", 100)],
        roofs=[("roof_black", 100)],
        doors=[("door_blue", 40), ("door_green", 30), ("trim_white", 30)],
        care=350,
    ),
}

ORDER = ["classical", "chalet", "jugend", "functionalist", "postwar", "seventies", "eighties"]


def era_for(year, key=0):
    """The era a part installed in this year comes from. Where eras overlap, the seed decides,
    leaning towards the newer one as the years go on."""
    live = [name for name in ORDER if ERAS[name]["years"][0] <= year <= ERAS[name]["years"][1]]
    if not live:
        return ORDER[0] if year < ERAS[ORDER[0]]["years"][0] else ORDER[-1]
    if len(live) == 1:
        return live[0]
    pairs = []
    for name in live:
        start, end = ERAS[name]["years"]
        pairs.append((name, 1 + max(0, year - start)))
    return weighted(key, pairs)


# Stylisation: how far shapes are pushed. Per mille, millimetres, tenths of a degree.
STYLES = {
    "gentle": dict(band=300, lap=22, pitch=1050, eave=1100, win=1050, frame=130, lean=6, sag=60, bow=0, jitter=35, tilt=6, chamfer=12, chimney=1000, kick=600),
    "strong": dict(band=375, lap=32, pitch=1160, eave=1350, win=1120, frame=170, lean=22, sag=220, bow=60, jitter=70, tilt=14, chamfer=22, chimney=1300, kick=1000),
    "stronger": dict(band=500, lap=46, pitch=1300, eave=1700, win=1220, frame=230, lean=26, sag=260, bow=60, jitter=80, tilt=16, chamfer=30, chimney=1600, kick=1000),
    "wild": dict(band=500, lap=46, pitch=1300, eave=1700, win=1220, frame=230, lean=45, sag=480, bow=140, jitter=120, tilt=26, chamfer=35, chimney=1600, kick=1000),
}
