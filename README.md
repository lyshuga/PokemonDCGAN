# PokemonDCGAN

The project is assigned to the topic of Generating Pokemon images using Deep Convolutional GAN. Convolution layers allow to identify and generate precise representation fo the image. Though in DCGAN it is the main obstacle as far as training two networks (Generator and Discriminator) is a pretty sensitive process.

Eventually I came out that Generator should be pretty simple, meanwhile, Discriminator should be complex in order to prevent constant Discriminator winning.

That is why Discriminator is:

![alt text](https://i.imgur.com/idlEYUQ.png)

And Generator is much simplier:

![alt text](https://i.imgur.com/BE5hcMc.png)

During the training with augmentation, assigning different values for parameters and changing architecture, I have got such results:

![alt text](https://i.imgur.com/T55m44Z.png)


Though not as impressive as expected. The future plan is to make the generator more complex while trying to keep the discriminator the same.
