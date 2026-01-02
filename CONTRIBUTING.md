# Contributing to Awesome Failed ML Experiments 🤝

First off, thank you for considering contributing! Every failure shared is a lesson learned for the entire ML community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Submit a Failure](#how-to-submit-a-failure)
- [Submission Template](#submission-template)
- [Review Process](#review-process)
- [Style Guide](#style-guide)
- [Categories](#categories)
- [Getting Help](#getting-help)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to riteshrana36@gmail.com.

---

## How to Submit a Failure

### Step 1: Fork the Repository

Click the "Fork" button in the top right corner of this repository.

### Step 2: Create Your Submission File

1. Navigate to `submissions/YEAR/` (e.g., `submissions/2026/`)
2. Create a new markdown file with a descriptive name:
   - Format: `your_experiment_name.md`
   - Example: `bert_fine_tuning_on_small_dataset.md`
   - Use lowercase and underscores (no spaces!)

### Step 3: Fill Out the Template

Use the [submission template](#submission-template) below. **All fields are required!**

### Step 4: Submit a Pull Request

1. Commit your changes
2. Push to your fork
3. Open a Pull Request against the `main` branch
4. Fill out the PR template

### Step 5: Automated Review

Our GitHub Actions bot will automatically:
- ✅ Validate your markdown structure
- ✅ Check all links (no dead links allowed!)
- ✅ Detect duplicate submissions
- ✅ Verify code formatting

If everything passes, your PR will be **automatically merged**! 🎉

---

## Submission Template

Copy and paste this template into your submission file:

```markdown
---
title: "Your Experiment Title"
category: "Category Name"
date: "YYYY-MM-DD"
author: "Your Name"
github: "your-github-username"
---

# Your Experiment Title

## 📝 Description

A brief description of what you were trying to accomplish. (2-4 sentences)

## 🤖 Model / Algorithm

- **Model:** e.g., BERT, ResNet-50, XGBoost
- **Framework:** e.g., PyTorch, TensorFlow, scikit-learn
- **Architecture details:** Any modifications or custom layers

## 📊 Dataset

- **Name:** e.g., ImageNet, CIFAR-10, Custom Dataset
- **Size:** e.g., 50,000 images, 1M rows
- **Source:** Link to dataset or description if private

## ❌ What Failed

Describe specifically what went wrong. Be detailed!

- What behavior did you observe?
- What did you expect instead?
- When did you notice the failure?

## 🔍 Why It Failed

Your analysis of the root cause(s):

1. First reason
2. Second reason (if applicable)
3. Third reason (if applicable)

## 📈 Logs / Metrics

Include relevant logs, error messages, or metrics:

```
Paste your logs here
```

Or link to external resources:
- [Training logs](link)
- [Weights & Biases run](link)

## 💡 Lessons Learned

What did you learn from this failure?

1. First lesson
2. Second lesson
3. Third lesson

## 🔗 Related Resources

- [Link to paper](if applicable)
- [Link to code](if applicable)
- [Link to discussion](if applicable)
```

---

## Review Process

### Automated Checks

Your submission will be automatically validated for:

| Check | Description |
|-------|-------------|
| **Structure** | All required sections are present |
| **Links** | All URLs return valid responses |
| **Duplicates** | Not too similar to existing submissions |
| **Formatting** | Follows markdown best practices |

### Manual Review (If Needed)

If automated checks fail, you'll receive feedback on what to fix. Common issues:

1. **Missing sections** - Ensure all template sections are filled
2. **Dead links** - Remove or fix broken URLs
3. **Duplicate content** - Make your submission unique
4. **Formatting issues** - Follow the exact template structure

---

## Style Guide

### Markdown

- Use ATX-style headers (`#`, `##`, `###`)
- Use fenced code blocks with language specifiers
- Keep lines under 120 characters when possible
- Use bullet points for lists

### Code Examples

If including code:
- Keep examples minimal and focused
- Use proper syntax highlighting
- Remove sensitive information (API keys, passwords)

### Writing

- Be honest and specific about failures
- Focus on learnings, not blame
- Use clear, technical language
- Proofread for typos

---

## Categories

Choose the most appropriate category for your submission:

| Category | Emoji | Description |
|----------|-------|-------------|
| Computer Vision | 🖼️ | Image classification, object detection, segmentation |
| Natural Language Processing | 📝 | Text classification, NER, translation, QA |
| Speech & Audio | 🔊 | Speech recognition, audio classification |
| Tabular Data | 📊 | Structured data, feature engineering |
| Reinforcement Learning | 🎮 | RL agents, reward shaping |
| Generative Models | 🧬 | GANs, VAEs, diffusion models |
| Time Series | ⏱️ | Forecasting, anomaly detection in sequences |
| Anomaly Detection | 🔍 | Outlier detection, fraud detection |
| Recommendation Systems | 📈 | Collaborative filtering, content-based |
| MLOps & Infrastructure | 🔧 | Deployment, scaling, monitoring |
| Other | 🤖 | Anything else! |

---

## Getting Help

- **Questions?** Open a [Discussion](https://github.com/ambicuity/awesome-failed-ml-experiments/discussions)
- **Bug in automation?** Open an [Issue](https://github.com/ambicuity/awesome-failed-ml-experiments/issues)
- **Direct contact:** riteshrana36@gmail.com

---

## Recognition

All contributors are recognized in our:
- Weekly summaries
- Annual "Best Failures" compilation
- Contributors list

Thank you for making the ML community better by sharing your failures! 🙏
