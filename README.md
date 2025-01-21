# Temporal Context Awareness (TCA) Framework for Securing LLMs

# Description
This repository contains the implementation of the Temporal Context Awareness (TCA) framework, a novel defense mechanism designed to protect Large Language Models (LLMs) from multi-turn manipulation attacks. These attacks exploit the conversational nature of LLMs, gradually building context across multiple turns to elicit harmful or unauthorized responses.

The TCA framework combines the following components to detect and mitigate adversarial tactics:

* Semantic Drift Analysis: Tracks shifts in conversation topics and intents.
* Cross-Turn Consistency Verification: Ensures alignment of user intent across conversational turns.
* Progressive Risk Scoring: Dynamically evaluates risks based on interaction, pattern, and historical risks.

## Features
* Implementation of risk evaluation metrics and security decision engine.
* Analysis and mitigation of common adversarial tactics, such as:
  Direct Requests
  Obfuscation
  Hidden Intentions
  Request Framing
  Output Format Exploitation
  Injection Attacks
  Echoing Tactics
* Support for multiple LLMs, including GPT, Claude, and Gemini.
* Dataset integration and automated testing on MHJ dataset scenarios. https://scale.com/research/mhj
* Modularized Python codebase for extensibility and experimentation.

## Usage
* Run simulations on adversarial conversations to evaluate and test the framework.
* Customize risk scoring weights and thresholds for your use case.
* Adapt the security decision engine for your organization's LLM deployment needs.
  

