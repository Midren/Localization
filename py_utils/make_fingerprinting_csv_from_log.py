import pandas as pd
import os

df = pd.DataFrame(columns=["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3", "Square"])
point_df = pd.DataFrame(columns=["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3", "Square", "Point"])

for root, dirs, files in os.walk("."):
    group_id = 0
    for filename in files:
        with open(filename, encoding="utf8", errors='ignore') as f:
            data_point = 0
            is_data = False
            for ind, line in enumerate(f.readlines()):
                if line.startswith("[INFO] RSSI sampling started"):
                    is_data = True
                    point_df = pd.DataFrame(columns=["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3", "Square", "Point"])
                if is_data:
                    if line.startswith("[INFO] RSSI values: "):
                        line = line[len("[INFO] RSSI values: "):]
                        i, j, k = map(int, line.strip().split())
                        point_df = point_df.append({"Server-RSSI-1": i, "Server-RSSI-2": j, "Server-RSSI-3": k, "Square": filename.split(".")[0], "Point": data_point}, ignore_index=True)
                if line.startswith("[INFO] RSSI sampling ended"):
                    is_data = False
                    df = pd.concat([df, point_df], sort=False)
                    data_point += 1

df.to_csv(filename + ".csv")
