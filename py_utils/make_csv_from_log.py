import pandas as pd

df = pd.DataFrame(columns=["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3"])

filename = "test"
group_id = 0
with open(filename) as f:
    for ind, line in enumerate(f.readlines()):
        if not len(line.strip()):
            group_id += 1
            continue
        if line.startswith("[INFO] RSSI values: "):
            line = line[len("[INFO] RSSI values: "):]
        i, j, k = map(int, line.strip().split())
        df = df.append({"Server-RSSI-1": i, "Server-RSSI-2": j, "Server-RSSI-3": k, "Group_id": group_id}, ignore_index=True)

df.to_csv(filename + ".csv")
