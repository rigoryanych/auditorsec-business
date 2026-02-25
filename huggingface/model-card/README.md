---
language:
  - en
license: apache-2.0
tags:
  - smart-contract
  - security
  - audit
  - web3
  - solidity
  - vulnerability-detection
pipeline_tag: text-classification
metrics:
  - accuracy
  - f1
---

# Audityzer Smart Contract Vulnerability Classifier

## Model Description

This model classifies Solidity smart contract code snippets for common vulnerability patterns. It is the AI backbone of the [Audityzer](https://github.com/romanchaa997/Audityzer) security platform.

**Task**: Multi-label vulnerability classification  
**Architecture**: Fine-tuned CodeBERT (microsoft/codebert-base)  
**Input**: Solidity function or contract snippet (tokenized)  
**Output**: Vulnerability label(s) with confidence scores

## Vulnerability Classes

| Label | Description |
|---|---|
| `reentrancy` | Reentrancy attack vector (SWC-107) |
| `integer_overflow` | Integer overflow/underflow (SWC-101) |
| `access_control` | Missing or broken access control (SWC-105) |
| `unchecked_call` | Unchecked return values (SWC-104) |
| `tx_origin` | tx.origin authentication abuse (SWC-115) |
| `timestamp_dep` | Block timestamp dependence (SWC-116) |
| `safe` | No vulnerability detected |

## Intended Use

- CI/CD pipeline integration for Web3 projects
- Pre-audit automated triage
- Security training and education
- Building larger audit pipelines (Audityzer)

## How to Use

```python
from transformers import pipeline

audit_classifier = pipeline(
    "text-classification",
    model="audityzer/smart-contract-vuln-classifier"
)

solidity_snippet = """
function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount);
    (bool success,) = msg.sender.call{value: amount}("");
    balances[msg.sender] -= amount;
}
"""

result = audit_classifier(solidity_snippet)
print(result)  # [{'label': 'reentrancy', 'score': 0.97}]
```

## Training Data

Trained on the **AuditorSEC Vulnerability Dataset** (see `audityzer/smart-contract-vuln-dataset`), comprising:
- 15,000+ labeled Solidity functions from public audits
- SWC Registry examples
- DeFi exploit post-mortems (Compound, Aave, Curve incidents)

## Evaluation Results

| Metric | Score |
|---|---|
| Accuracy | 0.91 |
| F1 (weighted) | 0.89 |
| Precision | 0.90 |
| Recall | 0.88 |

*Evaluated on held-out test set of 2,000 samples.*

## Limitations

- Optimized for EVM/Solidity; limited support for Vyper, Move, Rust (Solana)
- Context window: 512 tokens (truncates long contracts)
- False positive rate ~9% on heavily obfuscated code

## License

Apache 2.0 — free for commercial and research use.

## Citation

```bibtex
@software{audityzer2026,
  author = {Audityzer / AuditorSEC Team},
  title = {Audityzer Smart Contract Vulnerability Classifier},
  year = {2026},
  url = {https://huggingface.co/audityzer/smart-contract-vuln-classifier}
}
```
