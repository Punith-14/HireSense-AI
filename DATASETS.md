# HireSenseAI Datasets

Last updated: 2026-05-20

Datasets are stored or referenced under `datasets/`. The project should prefer pretrained models and lightweight inference before training custom models.

## Candidate Datasets

### FER2013

- Purpose: facial emotion recognition benchmarking and optional fine-tuning.
- Source: Kaggle FER2013 facial expression recognition dataset.
- Notes: grayscale face images across common emotion labels.
- Licensing: verify the active Kaggle dataset license before redistribution or training artifact publication.

### CK+

- Purpose: facial expression and emotion validation.
- Source: Extended Cohn-Kanade dataset.
- Notes: controlled expression sequences; useful for validation, less representative of webcam interview lighting.
- Licensing: academic/research licensing must be checked before use.

### Speech Emotion Datasets

- Purpose: speech emotion and hesitation research.
- Candidates: RAVDESS, CREMA-D, TESS.
- Notes: use for evaluation only unless licensing permits training and redistribution.

## Preprocessing Notes

- Keep raw downloads outside committed source control.
- Store preprocessing scripts separately from model inference services.
- Track label mappings and train/validation splits.
- Avoid training large custom TensorFlow models unless pretrained options fail project goals.

## Model Usage Notes

- Current local emotion inference uses FER 22.4.0.
- Current attention estimate uses MediaPipe face landmarks.
- Model objects must be cached and reused; never load TensorFlow-backed models per request or per frame.
