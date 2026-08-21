import json
from pathlib import Path

import anthropic
from pydantic import ValidationError

from config import API_KEY
from schema import InvestmentOpportunity


client = anthropic.Anthropic(api_key=API_KEY)


def render_prompt(document: str) -> str:
    prompt_path = Path("prompts/extract_v2.txt")
    prompt_template = prompt_path.read_text(encoding="utf-8")

    schema = json.dumps(
        InvestmentOpportunity.model_json_schema(),
        indent=2,
    )

    examples = """
Example 1

Document:
PT Sentosa Snacks manufactures packaged snack products for the Indonesian market.
The company generated Rp100 billion in revenue.
It is raising Rp25 billion in Series A funding.
The CEO is Raka Pranoto.

Output:
{
  "company_name": "PT Sentosa Snacks",
  "industry": "Food and Beverage",
  "funding_stage": "Series A",
  "funding_amount": 25000000000,
  "revenue": 100000000000,
  "ebitda": null,
  "key_risks": [],
  "management_team": [
    {
      "name": "Raka Pranoto",
      "role": "CEO"
    }
  ]
}

Example 2

Document:
PT Cloud Kerja provides subscription-based workflow software to business customers.
Revenue was Rp60 billion with EBITDA of Rp8 billion.
The company is seeking Rp20 billion in Series B financing.
The CEO is Maya Santoso.

Output:
{
  "company_name": "PT Cloud Kerja",
  "industry": "B2B Software",
  "funding_stage": "Series B",
  "funding_amount": 20000000000,
  "revenue": 60000000000,
  "ebitda": 8000000000,
  "key_risks": [],
  "management_team": [
    {
      "name": "Maya Santoso",
      "role": "CEO"
    }
  ]
}

Example 3

Document:
PT Klinik Sejahtera operates outpatient medical clinics in Indonesia.
The company recorded Rp45 billion in revenue.
No EBITDA or funding stage was disclosed.
The CEO is Dr. Indra Wijaya.

Output:
{
  "company_name": "PT Klinik Sejahtera",
  "industry": "Healthcare Services",
  "funding_stage": null,
  "funding_amount": null,
  "revenue": 45000000000,
  "ebitda": null,
  "key_risks": [],
  "management_team": [
    {
      "name": "Dr. Indra Wijaya",
      "role": "CEO"
    }
  ]
}

Example 4

Document:
Surya Atap develops and operates rooftop solar installations for commercial buildings.
The company generated Rp80 billion in revenue and Rp9 billion in EBITDA.
It is seeking Rp30 billion of growth capital.
The CEO is Fajar Nugroho.

Output:
{
  "company_name": "Surya Atap",
  "industry": "Solar Energy",
  "funding_stage": null,
  "funding_amount": 30000000000,
  "revenue": 80000000000,
  "ebitda": 9000000000,
  "key_risks": [],
  "management_team": [
    {
      "name": "Fajar Nugroho",
      "role": "CEO"
    }
  ]
}

Example 5

Document:
PT Kopi Rakyat operates a network of coffee shops across major Indonesian cities.
Revenue reached Rp55 billion.
The CEO is Anita Prasetyo.
No funding amount, EBITDA, or investment risks were provided.

Output:
{
  "company_name": "PT Kopi Rakyat",
  "industry": "Coffee Shops",
  "funding_stage": null,
  "funding_amount": null,
  "revenue": 55000000000,
  "ebitda": null,
  "key_risks": [],
  "management_team": [
    {
      "name": "Anita Prasetyo",
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
    