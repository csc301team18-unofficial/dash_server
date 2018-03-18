DROP SCHEMA IF EXISTS dashschema CASCADE ;
CREATE SCHEMA dashschema;

SET search_path TO dashschema;

-- This table collects a user's core personal information,
-- and a link to their Goals table entry.
-- This information is user-specified upon signup
-- All fields are mandatory
CREATE TABLE Users(
  user_id VARCHAR(15) PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  age int NOT NULL,
  weight_kgs int NOT NULL,
  dash_streak int NOT NULL,
  dash_score int NOT NULL
);

-- This table keeps track of a user's fitness goals, referring back to the User table
-- Progress to goals is shown on the user interface by analyzing
-- data specified here with respect the entries in the Food Entry table
-- All fields are mandatory
CREATE TABLE Goals(
  goal_id VARCHAR(15) PRIMARY KEY,
  user_id VARCHAR(15) NOT NULL REFERENCES Users (user_id),
  water_grams int NOT NULL,
  protein_grams int NOT NULL,
  carbs_grams int NOT NULL,
  fats_grams int NOT NULL,
  calories int NOT NULL
);

-- Meal_id represents a common grouping of food the user eats
-- on a regular basis, an optional feature designed to minimize the time
-- it takes to enter in habitual foods like "breakfast oatmeal with bananas", or
-- "Grandma's chicken noodle soup". When a user says a name of a meal, DASH will
-- search here rather than look up the phrase on Nutritics
-- Meals belong to and are unique to a user. One user's "Grandma's chicken noodle soup"
-- will not be recognized for another user who did not specify this meal name
-- All fields are mandatory
CREATE TABLE Meal(
  meal_id int PRIMARY KEY,
  user_id VARCHAR(15) NOT NULL REFERENCES Users (user_id),
  meal_name VARCHAR(100) NOT NULL,
  time_of_creation date NOT NULL
);


-- This table represents the food parts that make up a ready meal
-- Their nutritional values have been previously looked up in Nutritics
-- This is necessary because calling a meal via Google Voice will
-- bypass the Nutritics lookup calls
-- Nutritics_id is an optional field to account for "water" as an entry
CREATE TABLE Food_Entry(
  food_entry_id int PRIMARY KEY,
  time_of_creation date NOT NULL,
  user_id VARCHAR(15) NOT NULL REFERENCES Users (user_id),
  meal_id int REFERENCES Meal(meal_id),
  nutritics_id VARCHAR(15), -- OPTIONAL
  food_name VARCHAR(100),
  serving_size int NOT NULL, -- grams
  calories int NOT NULL,
  fats int NOT NULL,
  protein int NOT NULL,
  carbs int NOT NULL
);


-- A day_id and the time_of_creation organize all the food consumed in a day by a user
-- An entry can either be a pre-specified meal, or a food_entry to be looked up on Nutritics
-- Optional fields: nutritics_id, meal_id, food_entry_id
-- Optional fields here allow us to organize the datetime information related to users'
-- nutritional intake while simultaneously maintaining flexibility in data types collected,
-- and maintaining an easy-to-comprehend database schema
CREATE TABLE Daily_Food(
  day_id VARCHAR(15) PRIMARY KEY,
  time_of_creation date NOT NULL,
  user_id VARCHAR(15) NOT NULL REFERENCES Users (user_id),
  food_entry_id int REFERENCES Food_Entry (food_entry_id), -- one of the meal/food fields will be filled
  meal_id int REFERENCES Meal (meal_id)
);
