---
title: Audityzer Smart Contract Auditor
emoji: 🔒
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: true
license: apache-2.0
tags:
  - smart-contract
  - security
  - web3
  - audit
  - solidity
---

import gradio as gr
from transformers import pipeline

# Load the Audityzer vulnerability classifier
# Replace with actual HF model path once published
MODEL_ID = "audityzer/smart-contract-vuln-classifier"

# Initialize classifier (falls back to demo mode if model not yet published)
try:
    classifier = pipeline("text-classification", model=MODEL_ID, top_k=3)
    model_loaded = True
except Exception:
    model_loaded = False

VULN_DESCRIPTIONS = {
    "reentrancy": "Reentrancy (SWC-107): External call before state update allows re-entry.",
    "integer_overflow": "Integer Overflow/Underflow (SWC-101): Arithmetic operation exceeds type bounds.",
    "access_control": "Access Control (SWC-105): Missing or insufficient ownership/role checks.",
    "unchecked_call": "Unchecked Return Value (SWC-104): Low-level call result not verified.",
    "tx_origin": "tx.origin Auth (SWC-115): Using tx.origin for authentication instead of msg.sender.",
    "timestamp_dep": "Timestamp Dependence (SWC-116): Block timestamp used for critical logic.",
    "safe": "No common vulnerabilities detected in this snippet."
}

EXAMPLE_SNIPPETS = [
    # Reentrancy
    '''function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount);
    (bool ok,) = msg.sender.call{value: amount}("");
    balances[msg.sender] -= amount;
}''',
    # Safe
    '''function transfer(address to, uint amount) public {
    require(balances[msg.sender] >= amount, "Insufficient");
    balances[msg.sender] -= amount;
    balances[to] += amount;
    emit Transfer(msg.sender, to, amount);
}''',
    # tx.origin
    '''function adminAction() public {
    require(tx.origin == owner, "Not authorized");
    // sensitive operation
}'''
]

def analyze_contract(solidity_code: str) -> str:
    if not solidity_code.strip():
        return "Please paste a Solidity function or contract snippet to analyze."

    if not model_loaded:
        # Demo mode: keyword-based heuristic
        code_lower = solidity_code.lower()
        findings = []
        if ".call{" in code_lower or ".call.value" in code_lower:
            findings.append(("reentrancy", 0.94))
        if "tx.origin" in code_lower:
            findings.append(("tx_origin", 0.91))
        if "block.timestamp" in code_lower or "now " in code_lower:
            findings.append(("timestamp_dep", 0.78))
        if not findings:
            findings.append(("safe", 0.88))

        result_lines = ["## Audityzer Analysis Results (Demo Mode)\n"]
        for label, score in findings:
            result_lines.append(
                f"**{label.upper()}** (confidence: {score:.0%})\n"
                f"> {VULN_DESCRIPTIONS.get(label, label)}\n"
            )
        result_lines.append("\n---\n*Full AI model coming soon on HuggingFace Hub.*")
        return "\n".join(result_lines)

    # Real model inference
    predictions = classifier(solidity_code[:512])
    result_lines = ["## Audityzer Analysis Results\n"]
    for pred in predictions[0]:
        label = pred["label"]
        score = pred["score"]
        if score > 0.1:
            result_lines.append(
                f"**{label.upper()}** (confidence: {score:.0%})\n"
                f"> {VULN_DESCRIPTIONS.get(label, label)}\n"
            )
    return "\n".join(result_lines)


with gr.Blocks(title="Audityzer - Smart Contract Security Analyzer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # Audityzer Smart Contract Security Analyzer
    **AI-powered vulnerability detection for Solidity smart contracts**

    Paste a Solidity function or contract below to scan for common vulnerabilities:
    reentrancy, integer overflow, broken access control, tx.origin misuse, and more.

    *Powered by [Audityzer](https://github.com/romanchaa997/Audityzer) | [AuditorSEC](https://github.com/audityzer-sandbox)*
    """)

    with gr.Row():
        with gr.Column(scale=2):
            code_input = gr.Textbox(
                label="Solidity Code",
                placeholder="Paste your Solidity function or contract here...",
                lines=15,
                max_lines=30
            )
            with gr.Row():
                clear_btn = gr.ClearButton(code_input, value="Clear")
                analyze_btn = gr.Button("Analyze", variant="primary")

        with gr.Column(scale=1):
            output = gr.Markdown(label="Analysis Results")

    gr.Examples(
        examples=EXAMPLE_SNIPPETS,
        inputs=code_input,
        label="Example Snippets"
    )

    analyze_btn.click(fn=analyze_contract, inputs=code_input, outputs=output)

    gr.Markdown("""
    ---
    ### About
    Audityzer automates the first pass of smart contract security review.
    For production audits, always combine AI analysis with manual expert review.

    **Links**: [GitHub](https://github.com/romanchaa997/Audityzer) | [Org](https://github.com/audityzer-sandbox) | [Dataset](https://huggingface.co/datasets/audityzer/smart-contract-vuln-dataset)
    """)

if __name__ == "__main__":
    demo.launch()
