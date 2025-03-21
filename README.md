# Temporal Context Awareness (TCA) Framework for Securing LLMs

## Description

This repository contains the implementation of the **Temporal Context Awareness (TCA) framework** as described in our paper: [Full Paper on arXiv](https://arxiv.org/pdf/2503.15560). The TCA framework is a novel defense mechanism designed to protect Large Language Models (LLMs) from multi-turn manipulation attacks. These attacks exploit the conversational nature of LLMs by gradually building context across multiple turns to elicit harmful or unauthorized responses.

## Key Components

The TCA framework combines several robust components to detect and mitigate adversarial tactics:

- **Semantic Drift Analysis:** Tracks shifts in conversation topics and intents.
- **Cross-Turn Consistency Verification:** Ensures alignment of user intent across conversational turns.
- **Progressive Risk Scoring:** Dynamically evaluates risks based on interaction patterns and historical data.

## Features

- **Risk Evaluation Metrics and Security Decision Engine:** Implements advanced risk assessment and mitigation strategies.
- **Adversarial Tactic Analysis:** Detects tactics including:
  - Direct Requests
  - Obfuscation
  - Hidden Intentions
  - Request Framing
  - Output Format Exploitation
  - Injection Attacks
  - Echoing Tactics
- **Multi-LLM Support:** Compatible with popular LLMs such as GPT, Claude, and Gemini.
- **Dataset Integration:** Automated testing on scenarios from the MHJ dataset ([Scale AI’s work](https://scale.com/research/mhj)).
- **Modular Python Codebase:** Built for extensibility and experimentation.

## Getting Started

### Prerequisites

- Python 3.8 or later
- [List additional libraries or dependencies here]

### Installation

1. Clone the repository:
   ```bash
   git clone [<repository-url>](https://github.com/prashantkul/multi-turn-attack-defenses)
   cd multi-turn-attack-defenses

2. Install the required dependancies (you may wanna use uv)
  ```bash
    pip install -e . 
  ```

## Usage

Custom Risk Scoring: Adjust weights and thresholds for fine-grained risk evaluation.
Security Decision Engine: Tailor the decision logic to align with your security protocols.
Extendability: Easily incorporate additional components or data sources as needed.

## Citation

```bibtex
@inproceedings{TCA2025,
  author         = {Kulkarni, P. and Namer, A.},
  title          = {Temporal Context Awareness (TCA) Framework for Securing LLMs},
  booktitle      = {Proceedings of the IEEE Conference on Artificial Intelligence (CAI)},
  year           = {2025},
  eprint         = {2503.15560},
  archivePrefix  = {arXiv},
  primaryClass   = {cs.LG},
  url            = {https://arxiv.org/pdf/2503.15560}
}

  

