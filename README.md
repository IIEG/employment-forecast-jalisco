# Employment Forecast Jalisco

Employment forecast engine for the state of Jalisco, México.  

This repository contains the machine-learning engine used to 
forecast the number of insured  employees in the state of Jalisco. The forecasting
algorithm is base on 12 independent regression models to estimate the 
employment level for the next n-months (where n is the index of the model). 
Therefore, the algorithm is capable creating individual estimations for each
month to estimate a year in advance. The individual estimations are segregated into 
the following variables:
* Economic division
* Gender
* Age range
* Year
* Month

By grouping on the results (group_by) one can analyze the employment 
levels among different categories.  

## Setup and config

Please follow these instructions to configure the project.

**For Linux (debian-based)**

1. Open a terminal and clone this repository:
    * `git clone https://github.com/IIEG/employment-forecast-jalisco.git`
    * `cd employment-forecast-jalisco`
1. Create and edit the configuration files.
    * `cp conf/.env.example conf/.env`
    * `cp conf/data_processing.json conf/data_processing.json`
    * Edit the files with `vim conf/.env` and `vim conf/data_processing.json`.
1. Create and activate virtual environment.
    * `virtualenv --python=python3 venv`
    * `source venv/bin/activate`
1. Install the requirements.
    * `pip install -r requirements.txt`
1. Run the setup script.
    * `python setup.py`

**Note**: to exit the virtualenv type `deactivate` in the terminal. 

**For Windows 10**

* You can [install a WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) debian-based distro and follow the 
**linux** instructions. 

### Environment Variables (.env)

This script uses a configuration defined in a `conf/.env` file. 
This file contains the variables needed in order to boostrap the 
project and create the directory structure. You can create a workable 
configuration file by copying the contents of `conf/.env.example` and
adding editing the `CONNECTION_STRING` and `QUERY_STRING` according 
to your local configuration. 

### Data Processing Variables (data_processing.json)

The data processing transformations are stored in a `conf/data_processing.json`
file. These json is used in the `service/data_preparation` module. 
The suggested transformations are contained in a `conf/data_processing.json.example`
file. You can copy that file in order to have a working data processing config. 


## Run the Application

**General instructions** 

Activate the virtualenv and run: 
```text
python app.py {flag}
```
Where:
```text
    flag: represents the application mode (i.e., --load, --search, --production, --forecast)
```

**Description**

The application has different "running" modes:
* **load** : reads the data from an sql-engine and updates a cache folder to use in the following modes. 
* **search** : uses a random-search algorithm to find the best combination of hyperparamets for the model.
The top result is stored in a json-file in the `model` folder. 
* **production** : reads the hyperparameters form the prev. steps and trains a model with the complete dataset.
The hexadecimal representation of the binary files is stored in the `model` folder.
* **forecast** : creates a forcast for the next 12 months based of the last date available in the 
database and saves the result in `data/output` as a csv-file. 

**For Linux (debian-based)**

To run the application: 
1. Activate the virtualenv.
    * `source venv/bin/activate`
1. Run the app.
    * `python app.py --load`
    * `python app.py --search`
    * `python app.py --production`
    * `python app.py --forecast`

**For Windows 10**

* You can [install a WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) debian-based distro and follow the 
**linux** instructions. 

## Authors and contributions
Feel free to contribute to the code-base. 

For more information or questions contact the main authors.

* [Rodrigo Hernández Mota](https://www.linkedin.com/in/rhdzmota)

## License

Contact IIEG for more information. 