#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request
from flask_restful import Resource

from config import app, db, api, SMS_MESSAGES
from models import *
import re

class SMSProcessor(Resource):
     def post(self):
        data = request.get_json()
        phone_number = data.get("from")
        message = data.get("text")

        if not phone_number or not message:
            return {"status": "error", "message": "Missing phone number or text"}, 400

        message = message.strip().lower()

        if message.startswith("start#"):
            return {
                "status": "success",
                "response": self.handle_registration(phone_number, message)
            }, 200
        
        elif message.startswith("details#"):
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                return {"status": "error", "message": "User not registered"}, 400
            return {
                "status": "success",
                "response": self.handle_details(user, message)
            }, 200
        
        elif message.startswith("myself"):
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                return {"status": "error", "message": "User not registered"}, 400
            return {
                "status": "success",
                "response": self.handle_self_description(user, message)
            }, 200
        
        elif message.startswith("match#"):
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                return {"status": "error", "message": "User not registered"}, 400
            return {
                "status": "success",
                "response": self.handle_match_request(user, message)
            }, 200
        
        elif message.startswith("next"):
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                return {"status": "error", "message": "User not registered"}, 400
            return {
                "status": "success",
                "response": self.handle_next_matches(user)
            }, 200

        elif re.fullmatch(r"\d{10}", message):
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                return {"status": "error", "message": "User not registered"}, 400
            return {
                "status": "success",
                "response": self.handle_profile_request(user, message)
            }, 200
        
        elif message.startswith("describe "):
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                return {"status": "error", "message": "User not registered"}, 400
            return {
                "status": "success",
                "response": self.handle_describe_request(user, message)
            }, 200
        
        elif message.upper().startswith("YES"):
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                return {"status": "error", "message": "User not registered"}, 400
            return {
                "status": "success",
                "response": self.handle_interest_confirmation(user)
            }, 200
        
        else:
            return {
                "status": "error",
                "message": "Unsupported command"
            }, 400
         
     def handle_registration(self, phone_number, message):
        """Handle initial registration: start#name#age#gender#county#town"""
        try:
            parts = message.split('#')
            if len(parts) != 6:
                return SMS_MESSAGES['REGISTRATION_INVALID_FORMAT']
            
            _, name, age, gender, county, town = parts
            
            # Validate age, gender and check if the user exists
            age = int(age)
            if age < 18 or age > 80:
                return SMS_MESSAGES['REGISTRATION_INVALID_AGE']
            
            if gender.lower() not in ['male', 'female']:
                return SMS_MESSAGES['REGISTRATION_INVALID_GENDER']
            
            existing_user = User.query.filter_by(phone_number=phone_number).first()
            if existing_user:
                return SMS_MESSAGES['REGISTRATION_ALREADY_EXISTS'].format(name=existing_user.name)
            
            # Create new user
            user = User(
                name=name.title(),
                phone_number=phone_number,
                age=age,
                gender=gender.lower(),
                county=county.title(),
                town=town.title(),
                registration_level='basic'
            )
            
            db.session.add(user)
            db.session.commit()
            
            return SMS_MESSAGES['REGISTRATION_SUCCESS'].format(name=name.title())
            
        except ValueError:
            return SMS_MESSAGES['REGISTRATION_INVALID_AGE_FORMAT']
        except Exception as e:
            return SMS_MESSAGES['REGISTRATION_FAILED'].format(error=str(e))
        
     def handle_details(self, user, message):
        """Handle details registration: details#education#profession#marital#religion#ethnicity"""
        try:
            parts = message.split('#')
            if len(parts) != 6:
                return SMS_MESSAGES['DETAILS_INVALID_FORMAT']
            
            _, education, profession, marital, religion, ethnicity = parts
            
            # Validate marital status
            if marital.lower() not in ['single', 'married', 'divorced']:
                return SMS_MESSAGES['DETAILS_INVALID_MARITAL']
            
            # Create user details
            user_detail = UserDetail.query.filter_by(user_id=user.id).first()
            if not user_detail:
                user_detail = UserDetail(user_id=user.id)
            
            user_detail.education_level = education.title()
            user_detail.profession = profession.title()
            user_detail.marital_status = marital.lower()
            user_detail.religion = religion.title()
            user_detail.ethnicity = ethnicity.title()
            
            user.registration_level = 'details'
            
            db.session.add(user_detail)
            db.session.commit()
            
            return SMS_MESSAGES['DETAILS_PROMPT']
            
        except Exception as e:
            return SMS_MESSAGES['DETAILS_REGISTRATION_FAILED'].format(error=str(e))
        
     def handle_self_description(self, user, message):
        """Handle self description: MYSELF description"""
        try:
            description = message[6:].strip()
            
            if len(description) < 10:
                return SMS_MESSAGES['SELF_DESCRIPTION_TOO_SHORT']
            
            # Update user details
            user_detail = UserDetail.query.filter_by(user_id=user.id).first()
            if not user_detail:
                user_detail = UserDetail(user_id=user.id)
                db.session.add(user_detail)
            
            user_detail.self_description = description
            user.registration_level = 'completed'
            
            db.session.commit()
            
            return SMS_MESSAGES['SELF_DESCRIPTION_SUCCESS']
            
        except Exception as e:
            return SMS_MESSAGES['SELF_DESCRIPTION_FAILED'].format(error=str(e))
        
     def handle_match_request(self, user, message):
        """Handle match request: match#age#town"""
        try:
            parts = message.split('#')
            if len(parts) != 3:
                return SMS_MESSAGES['MATCH_INVALID_FORMAT']
            
            _, age_part, town = parts
    
            if '-' in age_part:
                age_start, age_end = map(int, age_part.split('-'))
            else:
                age_start = age_end = int(age_part)
            
            matches = self.find_matches(user, age_start, age_end, town.title())
            
            if not matches:
                return SMS_MESSAGES['MATCH_NO_RESULTS'].format(town=town.title())
            
            # Create match request
            match_request = MatchRequest(
                user_id=user.id,
                age_range_start=age_start,
                age_range_end=age_end,
                town=town.title(),
                total_matches=len(matches)
            )
            
            db.session.add(match_request)
            db.session.commit()
            
            # Store matches
            for i, match_user in enumerate(matches):
                profile_match = ProfileMatch(
                    match_request_id=match_request.match_request_id,
                    matched_user_id=match_user.id,
                    position=i
                )
                db.session.add(profile_match)
            
            db.session.commit()
            
            # Send first batch
            gender_term = "gentlemen" if user.gender == "female" else "ladies"
            response = SMS_MESSAGES['MATCH_SUCCESS'].format(
                count=len(matches),
                gender_term=gender_term
            ) + "\n\n"
            
            first_batch = matches[:3]
            for match_user in first_batch:
                response += f"{match_user.name} aged {match_user.age}, {match_user.phone_number}. "
            
            remaining = len(matches) - 3
            if remaining > 0:
                response += "\n\n" + SMS_MESSAGES['MATCH_NEXT_PROMPT'].format(
                    remaining=remaining,
                    gender_term=gender_term
                )
            
            return response
            
        except ValueError:
            return SMS_MESSAGES['MATCH_INVALID_AGE_FORMAT']
        except Exception as e:
            return SMS_MESSAGES['MATCH_FAILED'].format(error=str(e))
    
     def find_matches(self, user, age_start, age_end, town):
        """Find potential matches based on criteria"""
        opposite_gender = 'female' if user.gender == 'male' else 'male'
        
        matches = User.query.filter(
            User.gender == opposite_gender,
            User.age >= age_start,
            User.age <= age_end,
            User.town == town,
            User.id != user.id
        ).all()
        
        return matches
     def handle_next_matches(self, user):
        """Handle NEXT command to get more matches"""
        try:
            # Get active match requests
            match_request = MatchRequest.query.filter_by(
                user_id=user.id,
                is_active=True
            ).order_by(MatchRequest.created_at.desc()).first()
            
            if not match_request:
                return SMS_MESSAGES['NEXT_NO_ACTIVE_REQUEST']
            
            if not match_request.has_more_matches():
                return SMS_MESSAGES['NEXT_NO_MORE_MATCHES']
            
            # Get next batch of matches
            next_matches = ProfileMatch.query.filter_by(
                match_request_id=match_request.match_request_id
            ).offset(match_request.current_offset).limit(3).all()
            
            if not next_matches:
                return SMS_MESSAGES['NEXT_NO_MORE_MATCHES']
            
            response = ""
            for match in next_matches:
                response += f"{match.matched_user.name} aged {match.matched_user.age}, {match.matched_user.phone_number}. "
            
            # Updates pagination
            match_request.advance_pagination()
            
            remaining = match_request.total_matches - match_request.current_offset
            if remaining > 0:
                gender_term = "gentlemen" if user.gender == "female" else "ladies"
                response += "\n\n" + SMS_MESSAGES['MATCH_NEXT_PROMPT'].format(
                    remaining=remaining,
                    gender_term=gender_term
                )
            
            return response
            
        except Exception as e:
            return SMS_MESSAGES['NEXT_FAILED'].format(error=str(e))
        
     def handle_profile_request(self, user, phone_number):
        """Handle profile request when user sends a phone number"""
        try:
            requested_user = User.query.filter_by(phone_number=phone_number).first()
            
            if not requested_user:
                return "Profile not found. Please check the phone number."
            
            # Get user details and notify the requested person
            details = UserDetail.query.filter_by(user_id=requested_user.id).first()
            
            response = f"{requested_user.name} aged {requested_user.age}, {requested_user.county} County, {requested_user.town} town"
            
            if details:
                response += f", {details.education_level or 'N/A'}, {details.profession or 'N/A'}, {details.marital_status or 'N/A'}, {details.religion or 'N/A'}, {details.ethnicity or 'N/A'}"
            
            response += f". Send DESCRIBE {phone_number} to get more details about {requested_user.name}."
            
            self.notify_interest(requested_user, user)
            
            return response
            
        except Exception as e:
            return f"Failed to get profile: {str(e)}"
        
     def handle_describe_request(self, user, message):
        """Handle DESCRIBE phone_number request"""
        try:
            parts = message.split()
            if len(parts) != 2:
                return "Invalid format. Use: DESCRIBE phone_number"
            
            phone_number = parts[1]
            requested_user = User.query.filter_by(phone_number=phone_number).first()
            
            if not requested_user:
                return "Profile not found."
            
            details = UserDetail.query.filter_by(user_id=requested_user.id).first()
            
            if not details or not details.self_description:
                return f"{requested_user.name} has not provided a self description yet."
            
            pronoun = "himself" if requested_user.gender == "male" else "herself"
        
            return f"{requested_user.name} describes {pronoun} as {details.self_description}"
            
        except Exception as e:
            return f"Failed to get description: {str(e)}"
        
     def notify_interest(self, requested_user, interested_user):
        """Notify user that someone is interested"""
        gender = 'man' if interested_user.gender == 'male' else 'woman'
        pronoun_subject = 'he' if interested_user.gender == 'male' else 'she'
        pronoun_object = 'him' if interested_user.gender == 'male' else 'her'

        message = SMS_MESSAGES['INTEREST_NOTIFICATION'].format(
            name=requested_user.name,
            gender=gender,
            interested_name=interested_user.name,
            phone_number=interested_user.phone_number,
            pronoun_subject=pronoun_subject,
            age=interested_user.age,
            county=interested_user.county,
            pronoun_object=pronoun_object
        )

        notification = Message(
            sender_id=0,
            recipient_id=requested_user.id,
            phone_number=requested_user.phone_number,
            content=message
        )

        db.session.add(notification)
        db.session.commit()

#api.add_resource(SMSProcessor, '/sms')

@app.route('/')
def index():
    return '<h1>Project Server</h1>'


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tables created successfully")
    app.run(port=5555, debug=True)