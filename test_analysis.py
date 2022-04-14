from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import pandas as pd
from random import randrange

def n_laps(stint):
    laps = stint.get("laps", [])
    return len(laps)

def prepare_laps(laps):
    prepared_laps = []
    union_idx = None
    for lap in laps:
        lap.set_index('Distance', inplace=True)
        if union_idx is None:
            union_idx = pd.Index([])
        union_idx.union(lap.index)

    for lap in laps:
        lap.reindex(union_idx)
        prepared_lap = lap
        prepared_lap['Speed'] = lap['Speed'].interpolate()
        prepared_laps.append(prepared_lap)
    return prepared_laps

def _get_longest_stint(stints):
    if len(stints) < 1:
        return {}
    stints.sort(reverse=True,key=n_laps)
    stint = stints[0]
    stint["laps"] = prepare_laps(stint["laps"])
    return stint

def get_longest_stint(laps, compound=None, accurate=True):
    stints = {}
    for (n, lap) in laps:
        if compound is not None and compound != lap.Compound:
            continue
        if not accurate or lap.IsAccurate:
            stint = stints.get(lap.Stint, {})
            laps = stint.get("laps", [])
            l = lap.get_car_data().add_distance()
            laps.append(l)
            stint = {
                "stint": lap.Stint,
                "compound": lap.Compound,
                "laps": laps,
            }
            stints[lap.Stint] = stint
    return _get_longest_stint(list(stints.values()))

def get_average_lap(stint):
    if len(stint) < 1:
        return []
    # there must be a way to do this with pandas
    rows = []
    indices = []
    for idx, row in stint[0].iterrows():
        speeds = []
        indices.append(idx)
        for lap in stint:
            speeds.append(row['Speed'])
        rows.append([sum(speeds)/len(speeds)])
    return pd.DataFrame(rows, columns=['Speed'], index=indices)

def get_min_lap(stint):
    concat = pd.concat(stint)
    return concat.groupby(concat.index).min()

def get_max_lap(stint):
    concat = pd.concat(stint)
    return concat.groupby(concat.index).min()

def get_random_lap(stint):
    idx = randrange(0, len(stint))
    return stint[idx]


fastf1.plotting.setup_mpl()
fastf1.Cache.enable_cache('/app/.cache/')

pd.set_option("display.max_rows", None)

# load a session and its telemetry data
session = fastf1.get_session(2022, 'Australian Grand Prix', 'FP1')
session.load()

drivers = [
    {"name":"LEC","color":"red"},
    {"name":"SAI","color":"pink"},
    {"name":"VER","color":"blue"},
    {"name":"PER","color":"magenta"},
]

avg_laps = []
stints = {}
for driver in drivers:
    name = driver["name"]
    l = session.laps.pick_driver(name).iterlaps()
    stint = get_longest_stint(l, compound=None)
    avg_lap = get_average_lap(stint["laps"])
    avg_laps.append({
        "lap": avg_lap,
        "driver": name,
        "color": driver["color"],
        "compound": stint["compound"],
        "n_laps": len(stint["laps"]),
    })
#min_lap = get_min_lap(stint)
#max_lap = get_max_lap(stint)
#random_lap = get_random_lap(stint)


fig, ax = plt.subplots()
#print(avg_laps)
for lap in avg_laps:
    label = f'{lap["driver"]} avg - {lap["compound"]} ({lap["n_laps"]})'
    ax.plot(lap["lap"].index, lap["lap"]['Speed'], color=lap["color"], label=label)

#ax.plot(min_lap.index, min_lap['Speed'], color="blue", label='min')
#ax.plot(max_lap.index, max_lap['Speed'], color="red", label='max')
#ax.plot(sai_avg_lap.index, sai_avg_lap['Speed'], color="pink", label='SAI avg')
#ax.plot(lec_avg_lap.index, lec_avg_lap['Speed'], color="red", label='LEC avg')
#ax.plot(random_lap.index, random_lap['Speed'], color="magenta", label='random')

ax.set_xlabel('Distance in m')
ax.set_ylabel('Speed in km/h')

ax.legend()
plt.suptitle(f"Avg laps comparison \n "
              f"{session.event['EventName']} {session.event.year} FP3")

plt.show()
