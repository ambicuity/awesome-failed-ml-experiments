---
title: "BERT Fine-tuning on Small Dataset"
category: "Natural Language Processing"
date: "2026-01-01"
author: "Example Author"
github: "example-user"
---

# BERT Fine-tuning on Small Dataset

## 📝 Description

Attempted to fine-tune BERT-base for sentiment classification on a custom dataset of product reviews. The goal was to achieve >90% accuracy on binary sentiment classification (positive/negative).

## 🤖 Model / Algorithm

- **Model:** BERT-base-uncased
- **Framework:** PyTorch with Hugging Face Transformers
- **Architecture details:** Standard BERT-base with a classification head (768 -> 2)

## 📊 Dataset

- **Name:** Custom Product Reviews Dataset
- **Size:** 500 labeled examples (250 positive, 250 negative)
- **Source:** Manually scraped and annotated from e-commerce sites

## ❌ What Failed

The model showed severe overfitting after just 2 epochs:

- Training accuracy: 99.8%
- Validation accuracy: 52.3% (basically random)
- Loss curves diverged dramatically

The model was essentially memorizing the training set instead of learning generalizable patterns.

## 🔍 Why It Failed

1. **Dataset too small:** 500 examples is far too few for fine-tuning a 110M parameter model like BERT. The model needs thousands of examples to learn meaningful patterns.

2. **No data augmentation:** Did not apply any text augmentation techniques (back-translation, synonym replacement, etc.) to artificially increase dataset diversity.

3. **Learning rate too high:** Used default learning rate of 5e-5, which was too aggressive for such a small dataset, causing the model to quickly overfit.

## 📈 Logs / Metrics

```
Epoch 1/5:
  Train Loss: 0.693 -> 0.234
  Train Acc: 50.2% -> 89.4%
  Val Loss: 0.691 -> 0.712
  Val Acc: 51.0% -> 52.1%

Epoch 2/5:
  Train Loss: 0.234 -> 0.032
  Train Acc: 89.4% -> 99.8%
  Val Loss: 0.712 -> 1.234
  Val Acc: 52.1% -> 52.3%

Early stopping triggered due to validation loss increase.
```

## 💡 Lessons Learned

1. **Rule of thumb for fine-tuning:** Need at least 10x more examples than model parameters for effective fine-tuning. For BERT, this means thousands to tens of thousands of examples.

2. **Start with pre-trained sentiment models:** Instead of fine-tuning from scratch, use models already fine-tuned on sentiment (like `nlptown/bert-base-multilingual-uncased-sentiment`) and adapt.

3. **Use regularization techniques:** For small datasets, apply aggressive dropout, weight decay, and early stopping based on validation metrics.

4. **Data augmentation is crucial:** Back-translation, synonym replacement, and other augmentation techniques can effectively 10x your dataset size.

5. **Consider simpler models:** For very small datasets, classical ML approaches (TF-IDF + SVM) often outperform deep learning.

## 🔗 Related Resources

- [BERT paper: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- [A Survey of Data Augmentation for NLP](https://arxiv.org/abs/2105.03075)
- [ULMFiT paper on transfer learning for NLP](https://arxiv.org/abs/1801.06146)
