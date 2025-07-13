# Standard library imports

# Remote library imports
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Local imports

# Instantiate app, set attributes
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Define metadata, instantiate db
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

CORS(app)

SMS_MESSAGES = {
    # Registration messages
    'REGISTRATION_SUCCESS': "Your profile has been created successfully {name}. SMS details#levelOfEducation#profession#maritalStatus#religion#ethnicity to 22141. E.g. details#diploma#driver#single#christian#mijikenda",
    'REGISTRATION_INVALID_FORMAT': "Invalid format. Use: start#name#age#gender#county#town",
    'REGISTRATION_INVALID_AGE': "Age must be between 18 and 80",
    'REGISTRATION_INVALID_GENDER': "Gender must be 'male' or 'female'",
    'REGISTRATION_ALREADY_EXISTS': "You are already registered as {name}. Send match#age#town to find matches.",
    'REGISTRATION_FAILED': "Registration failed: {error}",
    'REGISTRATION_INVALID_AGE_FORMAT': "Invalid age. Please enter a valid number.",
    
    # Details registration messages
    'DETAILS_PROMPT': "This is the last stage of registration. SMS a brief description of yourself to 22141 starting with the word MYSELF. E.g., MYSELF chocolate, lovely, sexy etc.",
    'DETAILS_INVALID_FORMAT': "Invalid format. Use: details#education#profession#marital#religion#ethnicity",
    'DETAILS_INVALID_MARITAL': "Marital status must be 'single', 'married', or 'divorced'",
    'DETAILS_REGISTRATION_FAILED': "Details registration failed: {error}",
    'DETAILS_SKIP_OPTION': "You were registered for dating with your initial details. To search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams. E.g., match#23-25#Nairobi",
    
    # Self description messages
    'SELF_DESCRIPTION_SUCCESS': "You are now registered for dating. To search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams. E.g., match#23-25#Kisumu",
    'SELF_DESCRIPTION_TOO_SHORT': "Please provide a longer description of yourself (at least 10 characters)",
    'SELF_DESCRIPTION_FAILED': "Self description failed: {error}",

    # Match request messages
    'MATCH_SUCCESS': "We have {count} {gender_term} who match your choice! We will send you details of 3 of them shortly.To get more details about a person, SMS their number e.g., 0722010203 to 22141",
    'MATCH_NO_RESULTS': "Sorry, no matches found for your criteria in {town}. Try different age range or town.",
    'MATCH_INVALID_FORMAT': "Invalid format. Use: match#age#town or match#age-range#town",
    'MATCH_INVALID_AGE_FORMAT': "Invalid age format. Use numbers only.",
    'MATCH_FAILED': "Match request failed: {error}",
    'MATCH_NEXT_PROMPT': "Send NEXT to 22141 to receive details of the remaining {remaining} {gender_term}",

    # Profile request messages
    'PROFILE_DETAILS': "{name} aged {age}, {county} County, {town} town, {education}, {profession}, {marital}, {religion}, {ethnicity}. Send DESCRIBE {phone} to get more details about {name}.",
    'PROFILE_NOT_FOUND': "Profile not found. Please check the phone number.",
    'PROFILE_FAILED': "Failed to get profile: {error}",

    # Describe request messages
    'DESCRIBE_INVALID_FORMAT': "Invalid format. Use: DESCRIBE phone_number",
    'DESCRIBE_NOT_FOUND': "Profile not found.",
    'DESCRIBE_NO_DESCRIPTION': "{name} has not provided a self description yet.",
    'DESCRIBE_SUCCESS': "{name} describes themselves as {description}",
    'DESCRIBE_FAILED': "Failed to get description: {error}",
    
    # Interest notification messages
    'INTEREST_NOTIFICATION': "Hi {name}, a {gender} called {interested_name} {phone_number} is interested in you and requested your details. "
    "{pronoun_subject} is aged {age} based in {county}. Do you want to know more about {pronoun_object}? Send YES to 22141",
    'INTEREST_CONFIRMATION_SUCCESS': "{name} aged {age}, {county} County, {town} town, {education}, {profession}, {marital}, {religion}, {ethnicity}. Send DESCRIBE {phone} to get more details about {name}.",
    'INTEREST_NO_NOTIFICATIONS': "No pending interest notifications found.",
    'INTEREST_CONFIRMATION_FAILED': "Failed to process confirmation: {error}",

    }