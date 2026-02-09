# Product Pack Validation Rules (MVP)

This repository ships a minimal validator for Tech4Life Product Packs. The validator focuses on the MVP contract for Product Packs and is designed to be easy to extend.

## What is validated

### Pack discovery

* A Product Pack is any **top-level folder** containing a `README.md` file.

### Required sections (MVP)

The validator loads `rules/product_pack_rules.yml` and checks that each Product Pack contains:

* `README.md`
* `01-toil-registration/*.md`
* `03-ethics-statement/*.md`
* `04-licensing-readiness/*.md`

Optional folders (sell sheet, pitch deck, prototype status, royalty) are allowed and listed in the rules file for clarity.

### Product ID format

* The validator scans each pack README for the first `T4L-TOIL-` token.
* The Product ID must match: `^T4L-TOIL-\d{3}-[A-Z0-9]+$`.

### Date format

* Dates in registration or release docs (folders `01-toil-registration` and `06-product-release`, when present) must follow `YYYY-MM-DD`.
* Any other numeric date tokens such as `2024/01/01` or `01-01-2024` are reported as invalid.

### Legacy ID detection

* Legacy IDs matching `T4L-20YY-NNN` are **not allowed** unless the line explicitly includes `Legacy ID` or `Legacy IDs`.

## Running locally

From the repo root:

```bash
python tools/t4l_validate_pack.py ../products
```

If you want to validate the current repository contents instead:

```bash
python tools/t4l_validate_pack.py .
```

To validate a checked-out products repository in a `products/` folder:

```bash
python tools/t4l_validate_pack.py products
```

## Extending the rules

Update `rules/product_pack_rules.yml` to add new required or optional sections:

```yaml
required:
  - id: new-section
    description: New section docs
    paths:
      - 07-new-section/*.md
```

The validator will automatically enforce the new rule once it is listed as required.

## CI usage

The GitHub Actions workflow runs the validator against this repository by default. To validate the external `tech4life-beyond/products` repository, set the `PRODUCTS_REPO` environment variable in the workflow (or in repo secrets) to `tech4life-beyond/products` so the optional checkout step activates.
