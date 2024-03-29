# SnakeAI
SnakeAI is a package developed to provide an interactive tool for training neural networks in mastering the Snake game, using a genetic algorithm for the training.

The main functionality is:

- Play against one of the trained models
- Observe a model playing while showing the neural network responding to inputs
- Train new models by selecting the neural network architecture and configuration, as well as the genetic algorithm
- Generate statistics over the different trained models and compare them graphically
<br>

## Main menu
Once the app is started it will prompt the main manu, the different options correspond to those described above.
<br>
<br>
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./readme_resources/main_menu.png">
    <img src="./readme_resources/main_menu.png">
  </picture>
</p>
<br> 

## Play vs AI
Under this section we can play against one of the trained models, as well as configure some of the game setting as graphics interface, speed, grid size..

https://github.com/laguneroo/SnakeAI/assets/129681739/1d25c24f-3924-43c3-a830-b9662670b3cc

<br>

## Test Model
In this section we can test our trained models and see the strongest activations over the neural network. During this execution the app produces statistical data about the model that can be used to be compared with other models.

https://github.com/laguneroo/SnakeAI/assets/129681739/6405decc-d97f-45d0-9b55-1c6d864660ec

<br>

## Train Model Configuration
Prior to launching a model training we will be prompted with a configuration window consisting of three tabs:

- General
- Neural Network
- Genetic Algorithm

<br>

https://github.com/alvarott/SnakeAI/assets/129681739/88b15aaf-9d77-438f-b2db-34351da71600

<br>

### General
Under this tab we configure general settings:

 - **Model name          :** Model's name
 - **Game size           :** Grid size
 - **Cpu cores           :** Logic cpu's cores to use during training
 - **Vision              :** Numeric representation of distances to feed the model (binary or real)
 - **Previous population :** This option unlocks the possibility of selecting an existing population and continue its training, during every iteration of the training the best individual (model) and the current population it is saved to disk under the path **<installation_folder>/SnakeAI_data/**

### Neural Network
The next parameters of a dense neural network are configurable:

- **Hidden layers :**  List of comma separated integer values (index = layer, value = number of nodes)(e.i [40, 40] two layers of 40 nodes each)
- **Hidden initialization :** Hidden layers initilization function
- **Hidden activation :** Hidden layers activation function
- **Output initilization :** Output layer initialization function
- **Output activation :** Output layer activation function
- **Bias :** Include bias vector
- **Bias initialization :** Bias vector initialization

### Genetic Algorithm
The app implements a classic genetic algorithm, the following parameters are configurable:

- **Population :** Number of individuals
- **Selection :** Selection method during evolution process
- **Crossover:** Crossover method (specific parameters of the method are also configurable, i.e crossover_rate)
- **Mutation:** Mutation method (currently just Gaussian implemented)
- **Replacement:** Population replacement method

<br>

## Train Model
During the training we can monitor the progress of the process with data represented over plots, such as population average score and population average fitness among others. It is also possible to stop the training and check how the model is performing launching the game.

<br>

https://github.com/alvarott/SnakeAI/assets/129681739/a0543962-2e1a-4fdf-985d-a0715f85ae6f

<br>

## Statistics
In this section the stats produced during the models execution at the section **Test Model** can be selected and compared among other models.

<br>

https://github.com/alvarott/SnakeAI/assets/129681739/1be16372-c352-4781-acea-f95afe63bd05

<br>

## Installation
The app can be build with all its resources using the current **"setup.cfg"**. Once it is packaged and installed in a virtual environment it can be started calling **"python -m snake_ai.main"**.

It can also be installed downloading the folder **SnakeAI_installer** and executing the file **"windows_installer.bat"** (Python >= 3.11.* and internet conexion is required to automatically install dependencies using pip).

When the installation is completed, the installation folder will be allocated at the same folder where the file **"windows_installer.bat"** was. In this path we will doble-click to the file **"./SnakeAI/SnakeAI.vbs"** to start the app.

<br>

## Dependencies
This project make use of the following third-party libraries:

- Numpy
- Matplotlib
- Pygame
- Customtkinter
<br>

## Packing
The app can be packed for example using **"pyinstaller"** runing the following commands:

            
            pyinstaller --name "SnakeAI" --noconfirm --onedir --windowed \
            
            --add-data "<path_to_customtkinter>/env_packing/Lib/site-packages/customtkinter;customtkinter/" \ 
            
            --add-data "<path_to_SnakeAI_source_code>/SnakeAI/src/snake_ai;snake_ai"  \
            
            --icon "<path_to_icon>/app_icon1.ico" \ 
            
            "<path_to_SnakeAI_main_module>/main.py"

