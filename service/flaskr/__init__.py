import os
import glob
import time
import numpy as np
import xarray
from flask import Flask, request, send_from_directory
from flask_cors import cross_origin
import matplotlib.pyplot as plt


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/query', methods=['GET'])
    @cross_origin()
    def make_query():
        cleanup()

        start_date, end_date = request.args.get('start_date'), request.args.get('end_date')
        if start_date is not None and end_date is not None:
            return query(int(start_date), int(end_date))

        return 'failed'

    @app.route('/image', methods=['GET'])
    @cross_origin()
    def get_image():
        return send_from_directory('.', 'window.png')



    return app

def cleanup():
    files_to_clean = glob.glob(f'{os.getcwd()}/burn-window-*.nc')
    for f in files_to_clean:
        try:
            os.remove(f)
        except:
            print("Error while deleting file : ", f)

def query(start_date: int, end_date: int):
    print("Querying against netcdf.")
    with xarray.open_dataset("window.nc") as burn_windows_dataset:
        burn_windows = burn_windows_dataset.__xarray_dataarray_variable__
        flattened_window = xarray.DataArray(coords=[burn_windows.coords['lat'][:], burn_windows.coords['lon'][:]],
                                            dims=['lat', 'lon'])
        flattened_window.data = np.sum(burn_windows.data[start_date:end_date, :, :], axis=0)
        flattened_window = flattened_window.astype('uint32')

        fig, ax = plt.subplots()
        fig.patch.set_visible(False)
        ax.axis('off')
        plt.imshow(flattened_window, cmap=plt.cm.Reds_r)
        plt.close(fig)
        fig.savefig('window.png')
        return 'success'
