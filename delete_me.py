from debate import view_debate
import os


api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key

# sit = """Problem: I am at the store and am trying to decide whether to buy a shirt or a hat.
# Proposed Solution: I am probably going to buy a hat because it is hot outside.
# """

sit = """Problem: I am looking at a closed drawer 1 and I believe there is a pen inside of it. I want to check if there is a pen inside of it.
Proposed Solution: I am thinking about taking the pen from drawer 1.
"""

res = view_debate(sit)

print(res)