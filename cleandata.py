#%%
import pandas as pd


def save_csv(filename: str, data: pd.DataFrame):
    with open(filename, "w") as f:
        data.to_csv(f, ",", index=False)


# %%
games_data = pd.read_csv("./data/games_2_sample.csv")
tags = pd.read_csv("./data/applicationTags.csv", header=None)

# Keep appid and 4 tags
tags: pd.DataFrame = tags[[0, 1, 2, 3, 4]]
tags.columns = ["appid", "t1", "t2", "t3", "t4"]
tags = tags.dropna()
tags.reset_index(inplace=True, drop=True)

save_csv("./filtered/tags.csv", tags)

# %%
# drop playtime == 0
games_data = games_data[games_data["playtime_forever"] > 0]

# drop appids not in tag list
games_data = games_data[games_data["appid"].isin(tags["appid"])]

# %%
# save

games_data.dropna()
games_data.reset_index(inplace=True, drop=True)
games_data.columns=["steamid","appid","playtime_minutes"]

save_csv("./filtered/games_data.csv", games_data)

# %%
merged = games_data.merge(tags, how="inner")
merged.columns = ["steamid", "appid", "playtime_minutes", "t1", "t2", "t3", "t4"]
merged

# %%
save_csv("./filtered/merged.csv", merged)
# %%
