# import re

# import next_cvat


# def extract_code_blocks(markdown_text):
#     usage_sections = re.findall(r"```python(.*?)```", markdown_text, re.DOTALL)
#     return usage_sections


# def test_readme():
#     with open("README.md", "r") as f:
#         markdown_text = f.read()

#     code_blocks = extract_code_blocks(markdown_text)

#     for code in code_blocks:
#         exec(
#             code,
#             {
#                 "next_cvat": next_cvat,
#                 "__name__": "__main__",
#             },
#         )