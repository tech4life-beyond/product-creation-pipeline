# Product Creation Pipeline

This repository contains the official Tech4Life product development lifecycle frameworks used to convert ideas into TOIL-licensed products.

## Start Here

Begin with the pipeline stages below.

## Pipeline Stages

1. [Concept Definition](01-concept-definition/Concept_Definition_Framework.md)
2. [Team Formation](02-team-formation/Team_Formation_Framework.md)
3. [Design Frameworks](03-design-frameworks/Design_Frameworks.md)
4. [Prototype Status Framework](04-prototype-status-framework/Prototype_Status_Framework.md)
5. [Validation Process](05-validation-process/Validation_Process_Framework.md)
6. [Product Release](06-product-release/Product_Release_Framework.md)

## Relationship to the Ecosystem

- **TLOS** defines the operating system and governance layer.
- This repository defines the operational pipeline used by Product Cells.
- **TOIL** defines licensing and commercialization requirements.
- **Products** contains the published TOIL Product Packs.

## Scope

These frameworks are process standards. They do not contain private legal agreements or financial records.

## License

Tech4Life Open Impact License (TOIL) v1.0

## Automation (CI)

This repository includes a Product Pack validator used in CI. See [docs/VALIDATION_RULES.md](docs/VALIDATION_RULES.md) for the MVP rules and extension guidance.

Run the validator locally:

```bash
python tools/t4l_validate_pack.py --path ../products
```
