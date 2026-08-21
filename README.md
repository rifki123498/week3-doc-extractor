# Week 3 – Structured Document Extractor

A structured document extraction pipeline using Claude, Pydantic validation, prompt versioning, and golden-set evaluation.

## What It Does

The extractor converts unstructured investment opportunity documents into structured JSON containing:

- Company name
- Industry
- Funding stage
- Funding amount
- Revenue
- EBITDA
- Key risks
- Management team

The output is validated using Pydantic before being returned.

## Project Structure

- `schema.py` – Pydantic models for structured extraction
- `extractor.py` – Claude API call, prompt rendering, validation, and retry logic
- `prompts/` – Versioned extraction prompts
- `golden/` – Test documents and expected JSON outputs
- `score.py` – Golden-set evaluation script

## Prompt Iteration

### Prompt V1

The initial prompt focused on extracting the required fields into the defined JSON schema.

Golden-set result:

- Field accuracy: **94.4%**
- Documents passing: **5/9**

Most errors were caused by inconsistent industry classification.

### Final Prompt

The final prompt added clearer extraction rules, few-shot examples, and a constrained industry taxonomy.

Final golden-set result:

- Field accuracy: **100%**
- Documents passing: **9/9**

This improved industry classification while preserving accuracy across the other fields.

## Validation and Retry

LLM output is validated against the `InvestmentOpportunity` Pydantic model.

If validation fails:

1. The validation error is returned to the model.
2. The model is asked to correct its JSON.
3. The process retries up to the configured limit.
4. If all attempts fail, the extractor raises a clear `RuntimeError`.

The malformed `doc_10.txt` test correctly fails after 3 attempts instead of returning fabricated structured data.

## Running the Extractor

Activate the virtual environment and run:

```bash
python extractor.py

Built as part of the Week 3 structured extraction exercise.

## Key Learnings

- Structured outputs are more reliable when combined with Pydantic validation.
- Few-shot examples improve consistency for ambiguous fields such as industry.
- A constrained taxonomy can significantly improve classification accuracy.
- Golden-set evaluation makes prompt improvements measurable rather than subjective.
python extractor.py
