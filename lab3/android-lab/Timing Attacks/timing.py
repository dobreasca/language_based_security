from datetime import datetime
import re

regions = {
    "Skyrim": 803,
    "Morrowind": 384,
    "Hammerfell": 723,
    "Valenwood": 547,
    "Elsweyr": 427,
    "Cyrodiil": 1052,
}

cities = {
    "Skyrim": {
        "Riften": 113,
        "Whiterun": 375,
        "Windhelm": 342,
        "Solitude": 312,
        "Markarth": 149,
        "Falkreath": 255,
    },
    "Morrowind": {
        "Vivec": 247,
        "Mournhold": 345,
        "Balmora": 307,
        "Ald'ruhn": 128,
        "Blacklight": 387,
        "Narsis": 289,
    },
    "Hammerfell": {
        "Sentinel": 157,
        "Rihad": 286,
        "Taneth": 336,
        "Elinhir": 305,
        "Dragonstar": 356,
        "Hegathe": 220,
    },
    "Valenwood": {
        "Falinesti": 340,
        "Elden Root": 244,
        "Haven": 128,
        "Silvenar": 72,
        "Arenthia": 321,
        "Southpoint": 389,
    },
    "Cyrodiil": {
        "Anvil": 209,
        "Bruma": 305,
        "Bravil": 260,
        "Chorrol": 189,
        "Leyawiin": 245,
        "Cheydinhal": 326,
    },
    "Elsweyr": {
        "Rimmen": 129,
        "Riverhold": 336,
        "Orcrest": 302,
        "Dune": 285,
        "Senchal": 420,
        "Torval": 168,
    },
}

def parse_time(t):
    if "." not in t:
        return datetime.strptime(t, "%H:%M:%S")
    main, frac = t.split(".")
    frac = frac[:6].ljust(6, "0")
    return datetime.strptime(main + "." + frac, "%H:%M:%S.%f")

def diff_ms(t1, t2):
    return (t2 - t1).total_seconds() * 1000

def closest(measured, table):
    best_name = None
    best_value = None
    best_error = None
    for name in table:
        error = abs(measured - table[name])
        if best_error is None or error < best_error:
            best_name = name
            best_value = table[name]
            best_error = error
    return best_name, best_value, best_error

def average(values):
    total = 0
    count = 0
    for value in values:
        total += value
        count += 1
    if count == 0:
        return None
    return total / count

pattern=re.compile(
    r"User:(?P<user>\d+)\s*;\s*Type:(?P<type>\w+)\s*;\s*Message:(?P<msg>.*?)\s*;\s*MessageID:(?P<id>\d+)\s*;\s*Time:(?P<time>[0-9:.]+)"
)

events = []
current_events = {}

with open("messenger_logs.txt", "r") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            user = match.group("user")
            msg_id = match.group("id")
            event_type = match.group("type")
            timestamp = parse_time(match.group("time"))
            key = (user, msg_id)
            if event_type == "new_msg":
                if key in current_events and "new_msg" in current_events[key]:
                    events.append((user, current_events[key]))
                current_events[key] = {}
            if key not in current_events:
                current_events[key] = {}
            current_events[key][event_type] = timestamp
            if "new_msg" in current_events[key] and "server_ack" in current_events[key] and "receiver_ack" in current_events[key]:
                events.append((user, current_events[key]))
                del current_events[key]

per_user_server_times = {}
per_user_receiver_times = {}

for user, event in events:
    time_to_server = diff_ms(event["new_msg"], event["server_ack"])
    time_to_receiver = diff_ms(event["server_ack"], event["receiver_ack"])
    if user not in per_user_server_times:
        per_user_server_times[user] = []
    if user not in per_user_receiver_times:
        per_user_receiver_times[user] = []
    per_user_server_times[user].append(time_to_server)
    per_user_receiver_times[user].append(time_to_receiver)

for user in sorted(per_user_server_times):
    avg_server = average(per_user_server_times[user])
    avg_receiver = average(per_user_receiver_times.get(user, []))
    region, region_value, region_error = closest(avg_server, regions)
    print("User:", user)
    print("  average time-to-server:", round(avg_server, 2), "ms")
    print("  inferred region:", region, "(table:", region_value, "ms, error:", round(region_error, 2), "ms)")
    if avg_receiver is not None:
        city, city_value, city_error = closest(avg_receiver, cities[region])
        print("  average time-to-receiver:", round(avg_receiver, 2), "ms")
        print("  inferred city:", city, "(table:", city_value, "ms, error:", round(city_error, 2), "ms)")
    else:
        print("  no receiver_ack values found")

    print()