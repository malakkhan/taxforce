# Belastingdienst SME Tax Compliance ABM

An Agent-Based Model (ABM) simulating tax compliance behavior among Small and Medium Enterprises (SMEs).

## Overview
This model simulates the interaction between tax authorities and SMEs. It captures:
* **Rational Choice:** Decision-making based on audit rates and penalty multipliers.
* **Normative Filters:** The impact of tax morale and trust in authorities.
* **Social Influence:** How morale spreads through a network topology.
* **'Enforecement' Dynamics** The impact of audits, convenants and guidance (information provision).

## Installation
Open your terminal, go to the folder where you want to put the code:
```bash
cd target-folder
```
Clone the repository:
```bash
git clone https://github.com/malakkhan/taxforce.git
cd your-repo-name
```
  
## Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
To launch the interactive dashboard:
```bash
python server.py
```

## Model Parameters
- **N**: Total number of SME agents.
- **Audit Rate ($p_a$):** The probability of an agent being audited.
- **Penalty Multiplier:** The rate of fine applied to evaded tax.
- **Social Influence ($w$):** The weight of peer influence on individual tax morale.

## Agent Parameters
- **category**: Micro, Small, or Medium.
- **true_profit**: The actual taxable income ($W$) before tax.
- **tax_morale**: Intrinsic motivation to pay taxes ($\chi$).
- **trust**: Belief in the benevolence of authorities.
- **subjective_audit_prob**: The agent's perceived risk of being caught ($p_e$).
- **has_advisor**: Whether the SME employs a fiscal advisor ($F$).

## Push to GitHub
Open your terminal or command prompt and run these commands to upload your code:

```bash
# Add all new files
git add .

# Commit your changes (example)
git commit -m "Initial commit: Added SME Tax Compliance ABM modules"

# Push to the existing remote
git push origin main
```
