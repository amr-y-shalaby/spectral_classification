from preprocessor import setup_configs
import rasterio
import matplotlib.pyplot as plt
from scipy.stats import norm
import numpy as np
def classifier(classification_method:str):
    satellite_image_dict = setup_configs()
    b4_satellite_image = satellite_image_dict['b4_satellite_image']
    b2_satellite_image = satellite_image_dict['b2_satellite_image']
    b4_raster = rasterio.open(b4_satellite_image)
    b2_raster = rasterio.open(b2_satellite_image)
    b2_data = b2_raster.read(1)  # a single band image
    b4_data = b4_raster.read(1)  # a single band image
    print('Band 2 Satellite Image:{} has {} Pixels in the Rows by {} Pixels in the Columns.\n'.format(b2_satellite_image, b2_data.shape[0], b2_data.shape[1]))
    print('Band 4 Satellite Image:{} has {} Pixels in the Rows by {} Pixels in the Columns.\n'.format(b4_satellite_image, b4_data.shape[0], b4_data.shape[1]))

    if classification_method.upper() == 'MLE':
        print('Maximum Likelihood Estimation Selected. Using Band 4 for Classification.\n')
        water_pdf = norm.pdf(b2_data, loc=satellite_image_dict['b2_water_mean'], scale=satellite_image_dict['b2_water_sd'])
        vegetation_pdf = norm.pdf(b2_data, loc=satellite_image_dict['b2_vegetation_mean'], scale=satellite_image_dict['b2_vegetation_sd'])
        urban_pdf = norm.pdf(b2_data, loc=satellite_image_dict['b2_urban_mean'], scale=satellite_image_dict['b2_urban_sd'])
        class = np.array()
        for w in water_pdf:
            for v in vegetation_pdf:
                for u in urban_pdf:
                    if w == max(w, v, u):


    if classification_method.upper() == 'HISTOGRAM':
        print('Histogram-Based Classification Selected')
        plt.hist(b2_data, density=False)
        plt.title('Band 2 Histogram of Digital Numbers. Fewer Modes are Better')
        plt.savefig(satellite_image_dict['parent_directory'] + '/Output/b2_digital_numbers_histogram.png')
        plt.show()
        plt.hist(b4_data, density=False)
        plt.title('Band 4 Histogram of Digital Numbers. More Modes are Worse')
        plt.savefig(satellite_image_dict['parent_directory'] + '/Output/b4_digital_numbers_histogram.png')
        plt.show()

classifier(classification_method='MLE')