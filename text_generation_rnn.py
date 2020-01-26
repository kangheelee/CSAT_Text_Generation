# -*- coding: utf-8 -*-
"""pi_project_exam.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LwqE9lZEvkHUWTPWKFnHdnnIbD3ZnskA
"""

# 필요한 모듈 불러오기

from __future__ import absolute_import, division, print_function, unicode_literals

!pip install -q tensorflow-gpu==2.0.0-alpha0
import tensorflow as tf

import numpy as np
import os

# 1. 구글 드라이브에섯 기출 데이터셋 가져오기

from google.colab import drive
drive.mount('/content/gdrive')

# 2. 수능 기출 데이터 불러오기
# 3. 해당 경로의 데이터셋 열기 + 읽기 + utf-8로 해독하기

## text = open(f, 'rb').read().decode(encoding = 'utf-8')
text = open('/content/gdrive/My Drive/Colab Notebooks/proto3.txt', 'rb').read().decode(encoding = 'utf-8')

## 일괄적으로 좌우 공백 제거
text = text.strip()

# 4. 프로토 타입용 데이터의 길이 14만  
print("Length of text: {} characters".format(len(text)))

# 5. 불러온 텍스트의 상위 800개 단어를 확인해보기 (약 1개 지문의 길이)
print(text[:800])

# 6. 텍스트에서 중복되는 단어들 제거하기 == unique한 어휘만 뽑아내기
vocab = sorted(set(text)) 
print(len(vocab))

# 7. 단어 벡터화 하기

## 1) mapping character to numbers 
## 2) numbers to characters

# 7.1 유효한 단어들의 인덱스 추출 ==> 단어 : 인덱스 == 사전화 하여 단어를 인덱스로 저장
## 단어 : 인덱스 형태의 사전 생성
char2idx = {u:i for i,u in enumerate(vocab)}

## 인덱스 : 단어 형태의 배열 생성
idx2char = np.array(vocab)

print(char2idx)
print(idx2char)

# c는 텍스트 속의 단어를 의미 
# 8. 단어들의 인덱스로 만든 배열 (리스트)
text_as_int = np.array([char2idx[c] for c in text])

### 전처리 과정을 아직 별도로 시행하지 않은 상태
print(text_as_int)

print('{')

## 20개까지만 보기
## 7. 20개의 '단어 : 인덱스' 형태의 char 뽑아내기
for char, _ in zip(char2idx, range(20)):
  print(' {:4s}: {:3d},'.format(repr(char), char2idx[char]))

print(' ...\n}')

# 9. 실제 문장과 word2vec으로 제대로 연결 되어 있는지 확인 (13번째 글자까지만 뽑아냈음)
print ('{} ---- characters mapped to int ---- > {}'.format(repr(text[:13]), text_as_int[:13]))

# Prediction Task

## sequence에 따라서 어떠한 char가 다음 번에 올 확률이 가장 높을 것인지?
## RNN은 이전의 데이터까지도 보관하여 다음 번에 어떠한 char가 올 것인지 예측이 가능

# Creating training examples and targets

## seq_length, 모든 데이터들은 오른쪽으로 한칸 씩 이동한 상태로 평행상태 유지
## 따라서 모든 chunks는 seq_length + 1의 상태를 기본값으로 함
## input seq는 Hell, target seq는 ello 


# 1회의 input에 대한 최대 문장 길이 
seq_length = 100
examples_per_epoch = len(text) 

print(examples_per_epoch)

# 훈련 데이터 생성
# 10. 데이터셋 -> 훈련 가능한 텐서로 변환
char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)

# 11. 텐서 상태에서 상위 5개의 텐서를 보기
for i in char_dataset.take(5):
  print(idx2char[i.numpy()])

# batch method를 이용해서, 원하는 사이즈로 잘라 내기 
# 12. 훈련 시행을 하는 seq_length의 길이와 drop remainder True
sequences = char_dataset.batch(seq_length + 1,drop_remainder = True)

# 13. 훈련 가능한 텐서 살펴보기 (take와 numpy를 사용)
for item in sequences.take(5):
  print(repr(''.join(idx2char[item.numpy()])))
  
## 5문장, 1문장 당 100의 길이를 지님.

# 14. 입력 데이터 및 타겟 데이터 생성
def split_input_target(chunk):
  input_text = chunk[:-1]
  target_text = chunk[1:]
  return input_text, target_text

dataset = sequences.map(split_input_target)

## output
## (1) input_text와 같이 첫 배치의 맨 마지막을 제외한 100개
## (2) taret_text와 같이 첫 배치의 맨 앞을 제외한 100개
## (3) input_text와 같이 두 번째 배치의 맨 마지막을 제외한 100개
## (4) target_text와 같이 두 번째 배치의 맨 앞을 제외한 100개
for input_example, target_example in dataset.take(1):
    print ('Input data: ', repr(''.join(idx2char[input_example.numpy()])))
    print ('Target data:', repr(''.join(idx2char[target_example.numpy()])))

for i, (input_idx, target_idx) in enumerate(zip(input_example[:5], target_example[:5])):
  print("Step {:4d}".format(i))
  print(" input: {} ({:s})".format(input_idx, repr(idx2char[input_idx])))
  print(" expected output: {} ({:s})".format(target_idx, repr(idx2char[target_idx])))
  
  ## formatting에서 repr 함수를 사용하는 경우
  ## 문자열에 작은 따옴표가 붙음

# 15. 훈련 가능한 데이터셋으로 랜덤하게 셔플하기
BATCH_SIZE = 64
BUFFER_SIZE = 10000
dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder = True)
dataset

# 16. 모델 만들기

## tf.keras.Sequential: to define the model
## tf.keras.layers.Embedding: input layer, mappling the numbers of each character to a vector
## tf.keras.layers.GRU: RNN with size units = rnn_units
## tf.keras.layers.Dense: output layer, with vocab_size

vocab_size = len(vocab)
embedding_dim = 256
rnn_units = 1024

## 모델 생성하기, Embedding 층, LSTM층, DENSE 층
def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
  model = tf.keras.Sequential([
      tf.keras.layers.Embedding(vocab_size, embedding_dim,
                               batch_input_shape = [batch_size, None ]),
      tf.keras.layers.LSTM(rnn_units,
                          return_sequences = True,
                          stateful = True,
                           ## 사용할 활성화 함수 선택
                          recurrent_initializer = 'glorot_uniform'),
      tf.keras.layers.Dense(vocab_size)
  ])
  
  return model

# 17. 필요 hyper-parameters 적용
model = build_model(vocab_size = len(vocab),
                   embedding_dim = embedding_dim,
                   rnn_units = rnn_units,
                   batch_size = BATCH_SIZE)

# Try the model

for input_example_batch, target_example_batch in dataset.take(1):
  example_batch_predictions = model(input_example_batch)
  print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

model.summary()

# 18. 지정한 형태로 차원 변경
sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples = 1) # (batch_size, num_samples) 형태로 변환
print(sampled_indices.shape)
# 19. 차원 축소
sampled_indices = tf.squeeze(sampled_indices, axis = -1 ).numpy() # 지정한 축의 rank 감소 
print(sampled_indices.shape)

sampled_indices

print("Input: \n", repr("".join(idx2char[input_example_batch[0]])))
print()
print("Next Char Predictions: \n", repr("".join(idx2char[sampled_indices ])))

# Train the model

## optimizer와 loss function 적용

# 20. 손실 함수 sparse_categorical_crossentropy 사용, logits 계산 활성화
def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits = True  )

example_batch_loss = loss(target_example_batch, example_batch_predictions) ## 실제 값과 예측 값의 차이 정도
print("Predictions shape", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
print("scalar_loss:     ", example_batch_loss.numpy().mean())

model.compile(optimizer = 'adam', loss = loss)

# Configure checkpoints

# 21. 현재 디렉터리에 새로운 체크 포인트 경로 설정 (이름은 training_checkpoints)
checkpoint_dir = './training_checkpoints'
# 22. os 모듈을 이용해서 해당 경로에 체크 포인트 만들기
checkpoint_prefix = os.path.join(checkpoint_dir, 'ckpt_{epoch}')

# 23.checkpoint 콜백 함수로 실행
checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
filepath = checkpoint_prefix,
save_weights_only = True)

EPOCHS = 30
## callback을 사용해서, 정의한 함수의 인자를 다른 함수의 인자로 넘겨줌 = 즉시 실행 가능
history = model.fit(dataset, epochs = EPOCHS, callbacks = [checkpoint_callback])

# Generate text

## Restore the latest checkpoint

tf.train.latest_checkpoint(checkpoint_dir)

model = build_model(vocab_size, embedding_dim, rnn_units, batch_size = 1)

# 24. 체크 포인트의 weights 값을 불러오기
model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))

model.build(tf.TensorShape([1,None]))

model.summary()

# Prediction loop

## 먼저 시작될 단어를 선택한 이후 RNN이 초기화되고 만들어질 여러개의 단어를 세팅
## 다음에 올 예측된 단어의 분산을 "초기 단어"와 "RNN state"를 통해서 추출
## 예측된 단어의 인덱스를 categorical distribution을 통해 계산하고 예측된 단어를 모델의 다음 입력값으로 설정
## 이후 RNN model을 통해서 하나의 단어가 아닌 더 의미 있는 문맥을 추출, 모델의 예측에 대해 RNN이 계속해서 피드백을 반복
## 이전 이전 예측 단어보다 어떤 것이 더 나은 결과를 주는지 RNN은 반복 학습

# 텍스트 제작 함수
def generate_text(model, start_string):
  
  # 1000개의 단어 생성
  num_generate = 1000
  
  # 25. 입력 데이터 조정하기 (단어 -> 인덱스화) + 차원 추가
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)
  
  # 결과 보존용 저장소
  text_generated = []
  
  # Low temp results in more predictable text
  # High temp results in more surprising text
  # Experiment to find the best setting
  
  temperature = 1.0
   
  model.reset_states()
  for i in range(num_generate):
    predictions = model(input_eval)
    
    # 26. 차원 줄이기
    predictions = tf.squeeze(predictions, 0)
    predictions = predictions / temperature
    
    # 27. 지정한 차원으로 변경하기
    predicted_id = tf.random.categorical(predictions, num_samples = 1)[-1,0].numpy()
    
    
    # 예상 단어와 다음 예측 단어 사이의 chain 생성
    input_eval = tf.expand_dims([predicted_id], 0)
    text_generated.append(idx2char[predicted_id])
    
    
  return (start_string + ''.join(text_generated))

print(generate_text(model, start_string=u"Education"))



# Advanced: Customized Training 

## tf.GradientTape를 사용하여 모델 업그레이드 하기

## (1) RNN 초기화 이후 tf.keras.Model.reset_states method 사용

## (2) dataset을 iterate한 이후, 예측값을 계산

## (3) tf.GradientTape로 해당 문맥의 예측값과 손실값을 계산함 

## (4) tf.GradientTape.grads method를 사용하여 각각 모델의 weights와 biases에 대한 손실의 미분값을 계산

## (5) tf.train.Optimizer.apply_gradients method를 사용하여 최적화

model = build_model(
vocab_size = len(vocab),
embedding_dim = embedding_dim,
rnn_units = rnn_units,
batch_size = BATCH_SIZE)

## TODO 25. 최적화 하기 ADAM 
optimizer = tf.keras.optimizers.Adam()

@tf.function
## TODO 26. 강하법을 사용하여 손실값 최적화 하기
def train_step(inp, target):
  with tf.GradientTape() as tape:
    predictions = model(inp)
    loss = tf.reduce_mean(
    tf.keras.losses.sparse_categorical_crossentropy(target, predictions, from_logits = True))
  grads = tape.gradient(loss, model.trainable_variables)
  optimizer.apply_gradients(zip(grads, model.trainable_variables))
  
  return loss

# Training step
EPOCHS = 10

for epoch in range(EPOCHS):
  start = time.time()

  for (batch_n, (inp, target)) in enumerate(dataset):
    loss = train_step(inp, target)

    if batch_n % 100 == 0:
      template = 'Epoch {} Batch {} Loss {}'
      print(template.format(epoch+1, batch_n, loss))

  # saving (checkpoint) the model every 5 epochs
  if (epoch + 1) % 5 == 0:
    model.save_weights(checkpoint_prefix.format(epoch=epoch))

  print ('Epoch {} Loss {:.4f}'.format(epoch+1, loss))
  print ('Time taken for 1 epoch {} sec\n'.format(time.time() - start))

model.save_weights(checkpoint_prefix.format(epoch=epoch))



len(a)

