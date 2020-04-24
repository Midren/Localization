import heapq
import itertools
from collections import defaultdict

import pandas as pd
import numpy as np
import plotly.express as px


def get_samples_by_points_num(df, points):
    grouped = df.groupby(["Point"])
    ret_df = grouped.get_group(points[0])
    for i in points[1:]:
        ret_df = ret_df.append(grouped.get_group(i))
    ret_df.reset_index(drop=True)
    return ret_df


def split_data(df, points_num, train_part, validation_part, test_part):
    assert train_part + validation_part + test_part == 1
    division = (np.array(
        points_num*np.array([train_part, validation_part, test_part]))).astype(int)
    assert np.sum(division) == points_num
    for i in range(1, len(division)):
        division[i] += division[i-1]
    division = division[:-1]

    return itertools.chain.from_iterable(
        map(lambda data: (data.drop(columns=["Point", "Square", "Orientation"]), data["Square"]),
            map(lambda points: get_samples_by_points_num(df, points),
                np.split(np.random.permutation(np.arange(points_num)), division))))


def split_data_regression(df, points_num, train_part, validation_part, test_part):
    assert train_part + validation_part + test_part == 1
    division = (np.array(
        points_num*np.array([train_part, validation_part, test_part]))).astype(int)
    assert np.sum(division) == points_num
    for i in range(1, len(division)):
        division[i] += division[i-1]
    division = division[:-1]

    return itertools.chain.from_iterable(
        map(lambda data: (data.drop(columns=["Point", "Square", "Orientation", "x", "y"]), data[["x", "y"]]),
            map(lambda points: get_samples_by_points_num(df, points),
                np.split(np.random.permutation(np.arange(points_num)), division))))


def show_scores(model,X_test,Y_test):
    predicted = model.predict(X_test)
    print("Number of mislabeled points out of a total %d points : %d"% (X_test.shape[0], (Y_test != predicted).sum()))
    probabilities = model.predict_proba(X_test)
    selected = []
    for i in probabilities:
        d = dict()
        for x,y in enumerate(i):
            d[x]=y
        selected.append(d)
    topFive = [heapq.nlargest(5,d,key=d.get)for d in selected]
    failed = 0
    for x,y in enumerate(topFive):
        if Y_test.iloc[x] not in y:
            failed+=1
    print("Number of points not in top 5 predicted probabilities total points: %d; failed: %d"% (X_test.shape[0], failed))


def visualize_errors(model, X_train, y_train, X_test, y_test):
    predicted = model.predict(X_test)

    X_train["Square"] = y_train.apply(str)
    X_test["Square"] = y_test.apply(str)

    X_train["correct_predict"] = y_train.apply(lambda x: "train")
    X_test["correct_predict"] = (y_test == predicted)
    df_tmp = pd.concat([X_train, X_test], ignore_index=True )
    # Plotly visualization
    fig = px.scatter_3d(df_tmp, x="Server-RSSI-1",
                                y="Server-RSSI-2",
                                z="Server-RSSI-3",
                                color="Square",
                                symbol='correct_predict')
    fig = fig.update_traces(marker=dict(size=8,
                                  line=dict(width=1,
                                            color='DarkSlateGrey')),
                  selector=dict(mode='markers'))
    fig.show()
    X_train.drop(["correct_predict", "Square"], axis=1, inplace=True)
    X_test.drop(["correct_predict", "Square"], axis=1, inplace=True)


def show_scores_per_point(model, X_test, y_test):
    predicted = model.predict(X_test)
    results = defaultdict(int)
    for i in range(X_test.shape[0]):
        results[y_test.iloc[i]] += y_test.iloc[i] != predicted[i]

    print("Accuracy of classifier for each square: ", end="")
    for sq in range(len(results)):
        if sq % 3 == 0:
            print()
        print("%.2f" % (1-results[sq]/y_test.groupby(y_test).get_group(sq).shape), end=" ")
    print()


def calc_mean_df(df, merge_points_num=10):
    mean_df = pd.DataFrame(columns=df.columns)

    grouped_by_square = df.groupby(["Square"])
    for square_group in grouped_by_square.groups:
        grouped_by_point = grouped_by_square.get_group(square_group).groupby(["Point"])
        for point_group in grouped_by_point.groups:
            point = grouped_by_point.get_group(point_group)
            mean_df = mean_df.append(pd.DataFrame(
                np.mean(np.array([point.iloc[range(0, len(point), int(len(point)/merge_points_num))].values
                                  for i in range(merge_points_num)]), axis=0),
                columns=mean_df.columns))
    mean_df.reset_index(drop=True)
    return mean_df


def add_coordinates(df):
    square_to_top_left_corner_map = {
        "s0": (0, 400), "s1": (100, 400), "s2": (200, 400),
        "s3": (0, 300), "s4": (100, 300), "s5": (200, 300),
        "s6": (0, 200), "s7": (100, 200), "s8": (200, 200),
        "s9": (0, 100), "s10": (100, 100),"s11": (200, 100)
    }

    point_to_coord_map = {0: (20, -20), 1: (50, -20), 2: (80, -20),
                          7: (40, -50), 8: (50, -50), 9: (54, -50), 3: (80, -50),
                          6: (40, -80), 5: (50, -80), 4: (80, -80)
    }

    df[["x", "y"]] =  pd.DataFrame(df["Square"].map(square_to_top_left_corner_map).to_list(), columns=["x", "y"])

    df["x"] = df["x"] + df["Point"].apply(lambda x: point_to_coord_map[x//4][0])
    df["y"] = df["y"] + df["Point"].apply(lambda x: point_to_coord_map[x//4][1])
    return df
