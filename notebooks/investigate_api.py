# %%
import next_cvat

client = next_cvat.Client.from_env_file(".env.cvat.secrets")

client.list_projects()
# %%


project = client.list_projects()[0].fetch()
# %%

project.get_tasks()
# %%


# %%
