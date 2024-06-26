import numpy as np
import cv2
from sklearn.cluster import KMeans
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

def segment_image(image_path, k=4):
    im = cv2.imread(image_path)  # Reads an image into BGR Format
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    original_shape = im.shape
    
    # Flatten each channel of the image
    all_pixels = im.reshape((-1, 3))

    km = KMeans(n_clusters=k)
    
    # Using ThreadPoolExecutor to fit the KMeans model
    with ThreadPoolExecutor() as executor:
        future = executor.submit(km.fit, all_pixels)
        km = future.result()

    centers = km.cluster_centers_
    centers = np.array(centers, dtype='uint8')

    colors = []
    for each_col in centers:
        colors.append(each_col)

    new_img = np.zeros((all_pixels.shape[0], 3), dtype='uint8')

    # Iterate over the image
    for ix in range(new_img.shape[0]):
        new_img[ix] = colors[km.labels_[ix]]
    
    new_img = new_img.reshape(original_shape)
    return new_img

def segment_image_from_array(image_array, k=4):
    im = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    original_shape = im.shape
    
    # Flatten each channel of the image
    all_pixels = im.reshape((-1, 3))

    km = KMeans(n_clusters=k)
    
    # Using ThreadPoolExecutor to fit the KMeans model
    with ThreadPoolExecutor() as executor:
        future = executor.submit(km.fit, all_pixels)
        km = future.result()

    centers = km.cluster_centers_
    centers = np.array(centers, dtype='uint8')

    colors = []
    for each_col in centers:
        colors.append(each_col)

    new_img = np.zeros((all_pixels.shape[0], 3), dtype='uint8')

    # Iterate over the image
    for ix in range(new_img.shape[0]):
        new_img[ix] = colors[km.labels_[ix]]
    
    new_img = new_img.reshape(original_shape)
    return new_img

# Example usage
if __name__ == "__main__":
    image_path = 'path_to_your_image.jpg'
    segmented_image = segment_image(image_path, k=4)
    
    # Display the original and segmented images
    original_image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(original_image)
    plt.title('Original Image')
    
    plt.subplot(1, 2, 2)
    plt.imshow(segmented_image)
    plt.title('Segmented Image')
    
    plt.show()
