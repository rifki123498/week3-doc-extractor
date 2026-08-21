import json
from pathlib import Path

import anthropic
from pydantic import ValidationError

from config import API_KEY
from schema import InvestmentOpportunity


client = anthropic.Anthropic(api_key=API_KEY)


def render_prompt(document: str) -> str:
    prompt_path = Path("prompts/extract_v1.txt")
    prompt_template = prompt_path.read_text(encoding="utf-8")

    schema = json.dumps(
        InvestmentOpportunity.model_json_schema(),
        indent=2,
    )

    examples = """
Example 1

Document:
PT Alpha is an Indonesian consumer company.
The company generated Rp120 billion in revenue.
It is seeking Rp30 billion in Series A funding.
The CEO is Andi Pratama.

Output:
{
  "company_name": "PT Alpha",
  "industry": "Consumer",
  "funding_stage": "Series A",
  "funding_amount": 30000000000,
  "revenue": 120000000000,
  "ebitda": null,
  "key_risks": [],
  "management_team": [
    {
      "name": "Andi Pratama",
      "role": "CEO"
    }
  ]
}
"""

    return prompt_template.format(
        schema=schema,
        examples=examples,
        document=document,
    )


def call_llm(messages: list[dict[str, str]]) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        temperature=0,
        messages=messages,
    )

    return response.content[0].text


def extract(document: str, retries: int = 2) -> InvestmentOpportunity:
    messages = [
        {
            "role": "user",
            "content": render_prompt(document),
        }
    ]

    for attempt in range(retries + 1):
        raw = call_llm(messages)

        try:
            return InvestmentOpportunity.model_validate_json(raw)

        except ValidationError as error:
            if attempt == retries:
                break

            messages.extend(
                [
                    {
                        "role": "assistant",
                        "content": raw,
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Your JSON failed validation:\n{error}\n"
                            "Return corrected JSON only."
                        ),
                    },
                ]
            )

    raise RuntimeError(
        f"Extraction failed after {retries + 1} attempts."
    )


if __name__ == "__main__":
    sample_document = """
    PT Nusantara Foods is an Indonesian food and beverage company.
    The company generated Rp85 billion in revenue in 2025 and
    EBITDA of Rp12 billion.

    Nusantara Foods is seeking Rp20 billion in Series A funding
    to expand into new cities.

    The CEO is Budi Santoso and the CFO is Maya Putri.

    Key risks include high customer concentration and execution
    risk from rapid expansion.
    """

    result = extract(sample_document)

    print(result.model_dump_json(indent=2))
    