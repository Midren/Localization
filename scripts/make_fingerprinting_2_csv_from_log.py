import pandas as pd
import os

SAMPLE_PER_POINT = 100

df = pd.DataFrame(columns=["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3", "Server-RSSI-4", "Server-RSSI-5", "Square", "Point", "Orientation"])
point_df = pd.DataFrame(columns=["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3", "Server-RSSI-4", "Server-RSSI-5", "Square", "Point", "Orientation"])

for root, dirs, files in sorted(os.walk(".")):
    for filename in files:
        with open(filename, encoding="utf8", errors='ignore') as f:
            data_point = 0
            orientation = 0
            sample_num = 0
            is_data = False
            for ind, line in enumerate(f.readlines()):
                if line.startswith("[INFO] RSSI sampling started"):
                    is_data = True
                    point_df = pd.DataFrame(columns=["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3",  "Server-RSSI-4", "Server-RSSI-5", "Square", "Point"])
                if is_data:
                    if line.startswith("[INFO] RSSI values: "):
                        line = line[len("[INFO] RSSI values: "):]
                        rssi = list(map(int, line.strip().split()))
                        orientation = (sample_num % (4*SAMPLE_PER_POINT))//SAMPLE_PER_POINT
                        point_df = point_df.append({"Server-RSSI-1": rssi[0], "Server-RSSI-2": rssi[1], "Server-RSSI-3": rssi[2],  "Server-RSSI-4": rssi[3], "Server-RSSI-5": rssi[4], "Square": filename.split(".")[0], "Point": data_point, "Orientation": orientation}, ignore_index=True)
                if line.startswith("[INFO] RSSI sampling ended"):
                    is_data = False
                    df = pd.concat([df, point_df], sort=False)
                    sample_num += len(point_df)
                    data_point += 1

df.to_csv("fingerprinting.csv")
