# Enhancing Trust and Confidence in Law Enforcement through Data Science

![Sample Image](https://github.com/AlexRaudvee/JBG050_Group_8/blob/main/docs/metropolitain_photo.jpeg)

## Content

1. [Brief introduction](#description)
2. [Contributions](#contributions)
3. [Data](#data-dev)
4. [Files Structure](#files-dev)
5. [How To Run](#how-to-run)

## Description

In an era where trust and confidence in law enforcement are paramount, this project delves into the realm of data science to better understand the determinants and predictors of public trust in the police, focusing on the context of the United Kingdom. Traditionally, police forces have prioritized crime detection and prevention, but there's a growing recognition that fostering trust among the public is equally critical. Through advanced data analysis and modeling techniques, this project aims to uncover insights that can inform strategies to enhance trust and confidence in law enforcement agencies.

#### Key Questions

- What factors influence public trust and confidence in the police?
- How can data science methodologies help identify and predict trends in trust levels?
- What actionable insights can be derived to improve trust-building efforts by law enforcement agencies?

#### Stakeholders:
1. The **M**etropolitan **P**olice **S**ervice (**“The Met”**)
2. The **M**ayor’s **O**ffice for **P**olicing **a**nd **C**rime (**MOPAC**)

## Contributions
Contributions to this repository are welcome from data scientists, researchers, policymakers, and anyone passionate about leveraging data-driven approaches to strengthen the relationship between law enforcement agencies and the communities they serve. Whether it's data analysis, algorithm development, visualization, or policy recommendations, every contribution plays a vital role in advancing our understanding and fostering trust in the police.

Join us in the pursuit of building safer, more trusting communities through the power of data science.



## Data 

The PAS data can be loaded via [this link](https://www.dropbox.com/scl/fi/uvjzubkwblibf08qgfkm9/PAS_data_dictionaries_shared.zip?rlkey=96509v3r4zhiqir8ngi5ig7je&e=1&dl=0) 

## Files (dev)
1. `.streamlit` - file with configurations for our framework
2. `.vscode` - file with configurations for working through VScode, used only during development of the code
3. `app`Folder
    - `iframe_figures` - folder with images for application
    - `pages` - folder which contains all pages (comparison, crime, recommendations and responsiveness page)
    - `app_data_preprocessors.py` - this file contains all preprocessors for data which is used in our application
    - `app_func.py` - this file contains all high level functions that we use in our application
    - `home.py` - this is the scrip file which contains the code of the home page of our application
4. `artifacts` - folder with visualizations used during the data exploration
5. `data` Folder - contains all the data files which used during the functioning of the framework.
6. `Data_Exploration` Folder 

    - `exploration.py` - file in which we provide the first step to data exploration
    - `api_.ipynb` - file in which we do the extraction of data from api. (dev file)
    - `Demographics_exploration.ipynb` - file with the dev code for application pages
    - `PASeda.ipynb` - file with code for exploration of the PAS data
    - `Practicing1.ipynb` - file with the dev code for our application
7. `data_preprocessors` Folder - files in this folder are going to run during the first run of the application
8. `docs` Folder - this folder contains all the documents for GitHub repository (like images)
9. `functions` - this folder contains the files with low level functions that we use in our project.
10. `data_loader.py` - this file should be run during the first launch of the application.
11. `config.py` - file with configurations that should be changed in your environment. 
12. `.gitignore` - files which are going to be ignored during your push actions
13. `LICENSE` - license of the project (dev) just in case
14. `requirements.txt` - this file contains all requirements that you will need to run this application. 

## How to Run

1. Download this repository or clone
2. Create environment 
3. Load the retirements by using ```pip install -r requirements```
4. Create a `pas_data_ward_level` folder inside the `data` folder
5. Add PAS files in `pas_data_ward_level` in `data` folder, this files should be avaliable for you via [dropbox](https://www.dropbox.com/scl/fi/uvjzubkwblibf08qgfkm9/PAS_data_dictionaries_shared.zip?rlkey=96509v3r4zhiqir8ngi5ig7je&e=1&dl=0) which was set to groups.
6. Now you can run the dataloader, `DATALOADER_stage_1` and `DATALOADER_stage_2`, if you experience any experiences with `DATALOADER_stage_2`, just delete the file `PAS_T%26Cdashboard_to%20Q3%2023-24.xlsx` in `data` folder, and run again, if doesn't help, download given file manually [here](https://data.london.gov.uk/dataset/mopac-surveys). If you still have an error, we recomend you to run the files in the data_preprocessors manually one by one, in this way everything should work!
7. Then copy this to your current terminal of virtual environment and paste this into your terminal: `cd .venv/lib/python3.10/site-packages/streamlit/elements/` (assume that you use MACOS, if not, correct this line a bit)
8. Then run this command in your terminal: `sed -i '' 's/from altair.vegalite.v4.api import Chart/from altair.vegalite.v5.api import Chart/' arrow_altair.py`. Now you are ready to run the app
9.1. Then resturt your terminal such taht you come back to original path
9.2. Type the `streamlit run app/home.py` in cmd and press ENTER
10. The first launch can take a bit more time due to the fact that application is going to load even more files during the run and prepare them and save them.

[docs/metropolitain_photo.jpeg]: docs/metropolitain_photo.jpg
