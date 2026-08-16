# Donor Matching & Eligibility Prediction — Integration Guide

## What this script does

1. Takes a blood request (recipient's location + blood group)
2. Loads a donor dataset and filters it to compatible donors in the same city
3. Sends each remaining donor's data to a hosted prediction API, which returns
   their probability of donating this month
4. Returns donors sorted by that probability, highest first

## Requirements

```bash
pip install pandas requests
```

No local model files are needed — prediction happens via an API call to an
already-deployed service. You only need the donor dataset on your end.

## Input file: CSV

The script expects a **CSV** file, read via:

```python
data = pd.read_csv("/path/to/blood_donor_dataset.csv")
```

Update this path to point at wherever the donor dataset actually lives in
your environment. If your donor data currently lives somewhere else
(Google Sheet, JSON, database export), export it to `.csv` first — the
rest of the script assumes a CSV on disk.

### Required columns

The dataset **must** contain these exact column names:

| Column | Type | Description |
|---|---|---|
| `donor_id` | string/int | Unique identifier for the donor |
| `city` | string | Donor's city — must match the recipient's city string exactly (case-sensitive) |
| `blood_group` | string | One of: `O+`, `O-`, `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-` |
| `as_of_month` | int | Current calendar month as a number, 1–12 (e.g. January = 1) |
| `months_since_joined` | int | Months since the donor registered, relative to `as_of_month` |
| `recency_months` | int | Months since the donor's last donation |
| `frequency_total_donations` | int | Total number of donations the donor has completed |
| `eligible_this_month` | int (0 or 1) | Whether the donor is currently eligible. Rule: eligible if `recency_months > 2`. Use `1` for eligible, `0` for not |

**Column names are case-sensitive and must match exactly** — a mismatch
(e.g. `City` instead of `city`) will cause a `KeyError` when the script
filters the DataFrame.

## How the matching logic works

1. **Location filter**: keeps only donors where `city` matches
   `recipient_location` exactly.
2. **Blood compatibility filter**: keeps only donors whose blood type is
   compatible *as a donor* to the recipient's blood type, using standard
   donor compatibility rules (e.g. a recipient with `A+` can receive from
   `O-`, `O+`, `A-`, `A+`; a recipient with `AB+` can receive from anyone).
3. **Prediction**: each remaining donor's row is sent one at a time to the
   prediction API, which returns a probability of donating.
4. **Sort**: results are sorted by that probability, descending — highest
   first.

## The prediction API call

```python
requests.post(
    "https://blood-project-1.onrender.com/predict",
    json={
        "as_of_month": current_month,
        "months_since_joined": months_since_joined,
        "recency_months": recency,
        "frequency_total_donations": total_donations,
        "eligible_this_month": eligible
    }
)
```

- **Method**: `POST`
- **Endpoint**: `https://blood-project-1.onrender.com/predict`
- **Body**: JSON, with the 5 keys shown above — types must match the table
  above (`as_of_month` as an int 1–12, `eligible_this_month` as 0/1)
- **Response**: JSON containing a `"prediction"` key. Depending on how the
  model endpoint was last configured, this may come back as a raw
  probability (e.g. `0.73`) or as a `[P(class 0), P(class 1)]` pair (e.g.
  `[0.27, 0.73]`) — **confirm which shape it returns before relying on
  `response.json()['prediction']` directly**, since indexing into it
  (`['prediction'][1]`) would be needed in the pair case.
- Note: **first request after idle time will be slow** (10–30+ seconds) —
  this is a free-tier Render service, which sleeps after inactivity and
  needs to "wake up" on the first call. Don't assume a timeout means it's
  broken; retry once.

## Output format

```python
sorted_result = [
    {"d_0042": 0.81},
    {"d_0117": 0.76},
    {"d_0009": 0.63},
    ...
]
```

A list of single-key dicts, `{donor_id: probability}`, sorted highest
probability first — this is your ranked shortlist of who to notify.
