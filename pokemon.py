
import os
import numpy as np
from keras.layers import Input, Dense, Flatten, Dropout, Reshape, Concatenate, UpSampling2D
from keras.layers import BatchNormalization, Activation, Conv2D, Conv2DTranspose,MaxPooling2D,AveragePooling2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers import GaussianNoise
from keras.models import Model, Sequential
from keras.optimizers import Adam, SGD
from google.colab import files
from skimage import io
from skimage.transform import resize
import PIL.Image
import matplotlib.pyplot as plt
import time
import random

files.upload()

filename = "/root/.kaggle/kaggle.json"
os.makedirs(os.path.dirname(filename), exist_ok=True)
os.rename('/content/kaggle.json', '/root/.kaggle/kaggle.json')
!chmod 600 /root/.kaggle/kaggle.json
import kaggle

kaggle.api.authenticate()
kaggle.api.dataset_download_files('kvpratama/pokemon-images-dataset', path='/content/', unzip=True)
import zipfile
zip_ref = zipfile.ZipFile('/content/pokemon.zip', 'r')
zip_ref.extractall('/content/')
zip_ref.close()

output_img_shape = (64,64,3)
def getGenerator(input_noise):

  hid = Dense(4*4*256, activation='relu')(input_noise)    
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  hid = Reshape((4, 4, 256))(hid)

  hid = Conv2DTranspose(128, 5, strides=2, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  
  hid = Conv2DTranspose(64, 4, strides=2, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)

  hid = Conv2DTranspose(32, 5, strides=2, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  
                      
  hid = Conv2DTranspose(3, kernel_size=5, strides=2, padding="same")(hid)
  out = Activation("tanh")(hid)

  model = Model(inputs=input_noise, outputs=out)
  return model, out


def getDiscriminator(input_img):
  
  
  hid = GaussianNoise(0.1)(input_img)
  
  hid = Conv2D(16, kernel_size=3, strides=2, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  hid = Dropout(0.5)(hid)
  
  hid = Conv2D(32, kernel_size=3, strides=2, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  hid = Dropout(0.5)(hid)
  
  hid = Conv2D(64, kernel_size=3, strides=1, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  hid = Dropout(0.5)(hid)
  #32x32x64
  hid = Conv2D(128, kernel_size=5, strides=2, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  hid = Dropout(0.5)(hid)
  #16x16x128
  hid = Conv2D(256, kernel_size=5, strides=1, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  hid = Dropout(0.5)(hid)
  #8x8x256
  hid = Conv2D(512, kernel_size=5, strides=2, padding='same')(hid)
  hid = BatchNormalization(momentum=0.9)(hid)
  hid = LeakyReLU(alpha=0.1)(hid)
  hid = Dropout(0.5)(hid)
  
  hid = Flatten()(hid)
  hid = Dense(256, activation='relu')(hid)
  
  out = Dense(1, activation='sigmoid')(hid)

  model = Model(inputs=input_img, outputs=out)
#   model.summary()
  return model,out

def train():
  g_optimizer = Adam(0.0002, 0.5)
  d_optimizer = Adam(0.0002, 0.5)
  gen_in = Input(shape = (100,))
  gen, gen_out = getGenerator(gen_in)
  disc_in = Input(shape = output_img_shape)
  disc,disc_out = getDiscriminator(disc_in)
  
  disc.compile(loss='binary_crossentropy',
            optimizer=d_optimizer,
            metrics=['accuracy'])
  disc.trainable = False
  x = gen([gen_in])
  gan_out = disc([x])
  GAN = Model(inputs=[gen_in], output=gan_out)
  GAN.compile(optimizer=g_optimizer, loss='binary_crossentropy')
  return GAN, gen, disc
GAN, G, D = train()

path = r'/content/pokemon'

def load_images(img_shape):
  
  fileNames = [f for f in sorted(os.listdir(path))]
  images = []
  for f in fileNames:
    img = PIL.Image.open(path + '/' + f)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0 and item[3] == 0:
            newData.append((255, 255, 255, 1))
        else:
            newData.append(item)

    img.putdata(newData)
    images.append(resize(toRGB(np.array(img)), img_shape))
    
  images = np.array(images)
  return images
  
def toRGB(image):
  return image[:,:,[0,1,2]]
  
images = load_images((64,64))

batch_size = 40
half_batch = int(batch_size)
history = []
def save_samples():
  
  rows = 3
  columns = 3
  noises = np.random.normal(0,1,(rows*columns,100))
  gen_imgs = G.predict(noises)
  gen_imgs = gen_imgs * (-1)
  fig, axs = plt.subplots(rows, columns)
  count = 0
  for r in range(rows):
    for c in range(columns):
      img = gen_imgs[count,:,:,:]
      img = ((img - img.min())*255 / (img.max() - img.min())).astype(np.uint8)
      axs[r,c].imshow(img)
      axs[r,c].axis('off')
      count += 1
  today = datetime.datetime.today().strftime('%Y-%m-%d')
  fig.savefig('samples/%s/mnist_%d.png' % (today,epoch))
  plt.close()

from keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(rotation_range=90)
datagen.fit(images)

kk = datagen.flow(images, batch_size=40)

a = 0
for X_batch in datagen.flow(images, batch_size=40):
  a = a + 1
#   print(a)
  for i in range(0, 40):
    images = np.append(images, X_batch[i].reshape(64, 64,3))
    
  if a == 20:
    break
    

images = images.reshape(-1,64,64,3)

def generate_noise(n_samples, noise_dim):
  X = np.random.normal(0, 1, size=(n_samples, noise_dim))
  return X

def show_samples(batchidx):
  noise = generate_noise(6,100)
  prediction = G.predict(noise)
  fig = plt.figure()
  for i in range(6):
      plt.subplot(1,6,i+1)
      img = prediction[i,:,:,:]
      img = ((img - img.min())*255 / (img.max() - img.min())).astype(np.uint8)
      plt.imshow(img) 
      plt.axis('off')
  plt.show()
  plt.close()

from keras.preprocessing import image
import datetime
import shutil

isExist = os.path.isdir('/samples')
if not isExist:
  os.makedirs('/samples')

today = datetime.datetime.today().strftime('%Y-%m-%d')
isExist = os.path.isdir('samples/%s' % today)
if not isExist:
  os.makedirs('samples/%s' % today)
else:
  shutil.rmtree('samples/%s' % today)
  os.makedirs('samples/%s' % today)
next = 1
epochs = 300
for epoch in range(epochs):
#   d_loss = (0,0)
#   g_loss = 0
  for batch in range(int(len(images)/batch_size)):

    # ---------------------
    #  Train Discriminator
    # ---------------------
    
    indxs = np.random.randint(0, len(images),half_batch)
    imgs = images[indxs]
    
    noise = np.random.normal(0,1,(half_batch,100))
    generated = G.predict(noise)
    
    d_fake_loss = D.train_on_batch(imgs, np.ones((half_batch,1)))
    d_art_loss = D.train_on_batch(generated, np.zeros((half_batch,1)))
    d_loss = np.add(d_fake_loss,d_art_loss) * 0.5


    # ---------------------
    #  Train Generator
    # ---------------------
    
    g_loss_sum = 0
    for i in range(1):
      valid_y = np.ones((batch_size,1))
      noise = np.random.normal(0, 1, (batch_size, 100))
    
      g_loss_sum = g_loss_sum + GAN.train_on_batch(noise, valid_y)
    
    g_loss = g_loss_sum / 1
    if g_loss >= d_loss[0]:
      next = 2
    else:
      next = 1
    
  print ("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100*d_loss[1], g_loss))
  save_samples()
  show_samples(str(epoch))

show_samples('3')