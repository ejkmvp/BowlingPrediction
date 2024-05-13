
# Bowling Score Prediction with Keras and Pytorch

## Design
Keras' Functional API was used to design the models. Later on, I tinkered with Pytorch to try to get a better model

The models take each pin as a binary input, where a 1 represents the pin standing after a shot, and a 0 represents the opposite. There are $10 * x$ inputs to each model, where x represents the number of shots being accounted for.

The models output a single number between 0 and 1 that, when multiplied by 300, represents the expected final score. 

## Data Collection
About 8,000,000+ bowling games have been collected with no regards to bowling skill level.

Data was collected from LaneTalk's API. LaneTalk is a popular software suite used by bowling alleys to digitize scoring in real-time. Previously, this data was harvested from LaneTalk's matches feature. Some scripts have been included under the Collection folder.  
```GetGamesInformation.py``` - Extract game information from a list of Game IDs from LaneTalk  
```ScoreDetailGetAllShots.py``` - Extracts completed game pin configurations and final scores into a CSV  
```ConvertAllShotsCSVToDataset.py``` - Converts the CSV data into a more efficient format for training  

Of the 8,000,000+ games collected, only about 3,800,000 were fully completed games, had no edited frames, and were valid (pin counts properly added up to final score and pins didnt magically appear on the second shot). Unfortunately, this may add some bias to the model. Houses with error-prone pin machines or slick pin decks may not be fully represented in the dataset, which could bring about some bias.
Side-note: I'm a little concerned about how low this number is, and it makes me wonder if valid games are accidentally being discarded.

For the pytorch model, I wanted all the data to be loaded into the GPU so I further sorted it down to about 1.1 million games by removing all games that scored below 150. This makes the model best suited for leagues or tournaments.

LaneTalk also collects significant data on professionals, so in the future, I would like to train another set of models based on their performance.

## Usage (Keras)
As of now, there isnt really a frontend to the models. Instead, each model will have to loaded with Keras in a python environment. Then, a  $1$ x $(10*x)$ numpy array must be constructured for input. Note that the "LSB of each shot" (the first input) represents the 1-pin. 
```
game = 	       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,	//10 Pin Left
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,	//10 Pin Picked
		0, 0, 1, 0, 0, 1, 0, 0, 0, 1,	//3-6-10 Left
		0, 0, 0, 0, 0, 0, 0, 0, 0, 1,	//Only 6-10 picked
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,	//Strike
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,	//shot is all zeros because there is no shot after a strike
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,	//Strike
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
model = keras.saving.load_model("model-4Frames.keras")
inputArray = numpy.array(game).reshape(1, 120)
model.predict(inputArray)
```

## Accuracy
It's kinda accurate :). I don't have a whole lot of empirical data collected yet but when trained on the first 6 frames, it guessed within 10 pins of the correct score a bit under 40% of the time on a sample 500 games.
The pytorch model based on the first 6 frames has an R^2 of 0.72 on a separate test dataset, which is much better than a multiple linear regression model which had an R^2 of around 0.4

## Goals

- Make some sort of web app out of this.
- Maybe make some sort of chrome extension to integrate this into Lanetalk live scoring. This would be a nice addition to those watching live scoring for professional tournaments 
