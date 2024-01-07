import configparser
import os.path
import rasterio
import math
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

def setup_configs():
    config = configparser.ConfigParser()
    config.read('config.ini')
    save_locally = eval(config['save_files']['save_locally_flag'].title())
    parent_dir = str(config['save_files']['parent_dir'])
    satellite_gain = float(config['satellite_parameters']['gain'])
    satellite_offset = float(config['satellite_parameters']['offset'])
    path_radiance = float(config['satellite_parameters']['path_radiance'])
    atmosphere_transitivity = float(config['satellite_parameters']['atmosphere_transitivity'])
    solar_radiance = float(config['satellite_parameters']['solar_radiance'])
    zenith_angle = float(config['satellite_parameters']['zenith_angle'])
    channel = int(config['satellite_parameters']['channel'])
    cell_size = int(config['satellite_parameters']['cell_size'])
    satellite_image = parent_dir + '/Data/toronto_2011_band4.tif'

    if save_locally not in [True, False]:
        raise Exception(
            "save_locally in config.ini is set as {}. Only True or False is accepted.".format(save_locally))

    if atmosphere_transitivity > 1 or atmosphere_transitivity <= 0:
        raise Exception(
            "Atmosphere Transitivity in config.ini is set as {} which needs to be ∈ ( 0, 1 ].".format(
                atmosphere_transitivity))

    if zenith_angle > 90 or zenith_angle < 0:
        raise Exception(
            "Zenith Angle in config.ini is set as {} which needs to be ∈ [ 0, 90 ].".format(atmosphere_transitivity))

    if channel > 7 or zenith_angle < 1:
        raise Exception(
            "Satellite Instrument (Channel) Number in config.ini is set as {} which needs to be ∈ [ 1, 7 ].".format(
                channel))

    if cell_size != 30:
        raise Exception(
            "Cell Size in config.ini is set as {} which needs to be 30 for Landsat 7.".format(cell_size))

    if not os.path.isfile(satellite_image):
        raise Exception(
            "Error loading Toronto 2011 Band 4 Satellite Image!"
        )

    print('Parent Directory: ', parent_dir, '\n*****************************')
    print('Satellite Gain: ', satellite_gain, '\nSatellite Offset: ', satellite_offset, '\nPath Radiance: ', path_radiance,
          '\nAtmosphere Transitivity: ', atmosphere_transitivity, '\nSolar Radiance: ', solar_radiance, '\nZenith Angle: ',
          zenith_angle)

    incoming_solar_irradiance = round(atmosphere_transitivity * solar_radiance * math.cos(math.radians(zenith_angle)), 5)
    satellite_image_configs_dict = {'satellite_image': satellite_image, 'channel': channel, 'cell_size': 30,
                                    'gain': satellite_gain, 'offset': satellite_offset, 'path_radiance': path_radiance,
                                    'atmosphere_transitivity': atmosphere_transitivity, 'solar_radiance': solar_radiance,
                                    'zenith_angle': zenith_angle, 'incoming_irradiance': incoming_solar_irradiance,
                                    'parent_directory':parent_dir, 'save_locally':save_locally}

    print(satellite_image_configs_dict)
    print('Save Locally Flag is set to: {}\n*****************************'.format(save_locally))
    del satellite_image, channel, cell_size, satellite_gain, satellite_offset, path_radiance, atmosphere_transitivity, \
        solar_radiance, zenith_angle, incoming_solar_irradiance, save_locally, parent_dir
    return satellite_image_configs_dict

def compute_reflectance(satellite_image: str):
    raster = rasterio.open(satellite_image)
    data = raster.read(1)  # a single band image
    print('Satellite Image {} Rows by {} Columns.'.format(data.shape[0], data.shape[1]))
    satellite_image_dict = setup_configs()
    total_radiance = satellite_image_dict['offset'] + (np.multiply(data, satellite_image_dict['gain']))
    net_radiance = total_radiance - satellite_image_dict['path_radiance']
    net_irradiance = np.multiply(net_radiance, math.pi)
    reflectance = np.divide(net_irradiance, satellite_image_dict['incoming_irradiance'])
    reflectance = np.where(reflectance < 0, 0, reflectance)
    reflectance = np.where(reflectance > 1, 1, reflectance)
    img = Image.fromarray(reflectance)
    img.save(satellite_image_dict['parent_directory'] + '/Data/toronto_reflectance.tif')