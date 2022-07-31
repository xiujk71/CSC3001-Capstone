# CSC3001-Capstone
python dependancies:
scikit-learn
tensorflow
sqlite3

Generated datasets are already provided, hence this is optional.
Steps for dataset generation:
1. Run data_twit_prep.py -> calculate reuse distance
2. Run data_classify.py -> to generate Class10 dataset
3. Run data_classify_simple.py -> to generate IQR/Q1/Q3 dataset.
3.1 Manually change the last two csv.loc lines to obtain desired dataset.

ANN models are not provided. Must be trained before running benchmarks.
Steps for training & benchmarking ANN models:
1. Open ml_tf_train_notebook_<dataset>.ipynb
2. Run all to train for all 4 FCN models. Repeat for all step 1-2 for all datasets
3. Once model is obtained, open ml_benchmark_v2_<FCN_model>.ipynb
4. Run all to obtain benchmark results

SVM Model fitting and evaluation are on a single ipynb.
Steps for training & benchmarking SVM models:
1. Open ml_svm_train_<dataset>_AIO.ipynb
2. Run all to train and obtain benchmarks.

Run presentation demo:
1. Run ml_svm_linear_demo.
2. Key in id and key_value to query.
3. Will start training every 5 queries.
