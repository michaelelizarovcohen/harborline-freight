# notebooks/

Exploratory analytics owned by the Data team (Samira Haddad).

| Notebook | Purpose |
|---|---|
| `churn_analysis.ipynb` | Shipper churn by cohort; cancellation-note themes via LLM classification |
| `lane_pricing_exploration.ipynb` | Lane-level pricing research for the v1.1 rate cards |

## Ground rules

* Data lives in `notebooks/data/` (gitignored). Pull exports from
  `s3://harborline-analytics-exports/` with your SSO profile.
* **Clear outputs before committing** (`jupyter nbconvert --clear-output --inplace *.ipynb`)
  — outputs can contain customer data or anything you printed, including environment
  variables. Notebook outputs are scanned by gitleaks like any other file.
* API keys come from environment variables (`OPENAI_API_KEY`, etc.). Never assign keys in a cell.
* Pin heavy dependencies in `requirements-notebooks.txt` if you add new ones.
