# %%
import next_cvat

client = next_cvat.Client.from_env_file(".env.cvat.secrets")

projects = client.list_projects()
# %%


# %%
