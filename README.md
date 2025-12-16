# Cross-Age Face Verification & Age Estimation

This project explores face analysis using the **FG-NET Aging Dataset**. It implements a dual-pipeline system: a Deep Learning model to estimate the age of a subject and a verification system to identify if two images belong to the same person despite significant age gaps.

## 🚀 Key Features

### 1. Age Estimation (Regression)
* **Model:** ResNet50 (Transfer Learning from ImageNet).
* **Architecture:** The base model is frozen (excluding the last 50 layers) to retain feature extraction capabilities while fine-tuning for age features.
* **Custom Head:** Added Global Average Pooling, a 256-unit Dense layer with ReLU, Dropout (0.3) for regularization, and a linear output layer.
* **Preprocessing:** Stratified splitting ensures all age groups (bins of 0-5, 5-10, etc.) are represented in training.

### 2. Cross-Age Face Verification
* **Library:** [DeepFace](https://github.com/serengil/deepface)
* **Model:** FaceNet512
* **Methodology:** Calculates the cosine/euclidean distance between face embeddings to determine similarity.
* **Metrics:** Evaluates performance using ROC-AUC and Accuracy scores on positive/negative pairs.

## 📂 Dataset
**Dataset Used:** [FG-NET Aging Dataset](https://yanweifu.github.io/FG_NET_data/)
* Contains 1,002 images of 82 subjects.
* Images span ages 0 to 69 years, making it ideal for age-invariant face recognition.
* *Note: This project assumes the dataset is located at `/kaggle/input/fgnet-dataset/FGNET/images`.*

## 🛠️ Tech Stack
* **Frameworks:** TensorFlow / Keras
* **Face Analysis:** DeepFace
* **Data Handling:** Pandas, NumPy, OpenCV
* **Visualization:** Matplotlib
* **Utilities:** Scikit-Learn (for metrics and splitting)

## ⚙️ Installation

```bash
# Clone the repository
git clone [https://github.com/YourUsername/Cross-Age-Face-Verification.git](https://github.com/YourUsername/Cross-Age-Face-Verification.git)
cd Cross-Age-Face-Verification

# Install dependencies
pip install tensorflow deepface opencv-python pandas matplotlib scikit-learn tqdm
