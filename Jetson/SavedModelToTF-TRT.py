import tensorflow as tf
from tensorflow.python.compiler.tensorrt import trt_convert as trt
from PIL import Image
import numpy as np

print("starting")

folder = "./models/"
input_saved_model_dir = folder + 'Model_1.6m_RGB'
output_saved_model_dir = input_saved_model_dir + '_TRT'

conversion_params = trt.DEFAULT_TRT_CONVERSION_PARAMS
conversion_params = conversion_params._replace(max_workspace_size_bytes=(1 << 30))
conversion_params = conversion_params._replace(precision_mode="FP16")
conversion_params = conversion_params._replace(maximum_cached_engines=16
                                               )

converter = trt.TrtGraphConverterV2(
    input_saved_model_dir=input_saved_model_dir,
    conversion_params=conversion_params)
converter.convert()
print("converted, building")


def input_fn():
    for i in range(1, 11):
        image = np.array(Image.open("images/" + str(i) + ".png"))
        image = image[170:, :]
        print(image.shape)
        # image = np.dot(image[..., :3], [0.299, 0.587, 0.114])
        image = image.reshape(1, image.shape[0], image.shape[1], 3)
        image = image.astype('float32') / 255
        print(image.shape)
        yield image,


converter.build(input_fn=input_fn)
print("built, saving")

converter.save(output_saved_model_dir)
print("Saved")



