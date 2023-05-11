from flask import Blueprint, jsonify, request, current_app
from concurrent.futures import ThreadPoolExecutor
import openai
from flask_cors import cross_origin, CORS

from .models import Campaign
from .config import ProductionConfig


nicer_api = Blueprint('nicer_api', __name__)
CORS(nicer_api)

executor = ThreadPoolExecutor(10)
results = {}
MODEL = 'gpt-3.5-turbo'


def openai_get_campaign_insights(campaign : Campaign, api_key: str):
    # openai.api_key = api_key

    # completion = openai.ChatCompletion.create(
    #     model=MODEL,
    #     messages=[{
    #         "role": "user","content": "Hello world"
    #     }]
    # )

    return {
        'name': campaign.name,
        'start_date': campaign.start_date,
        'end_date': campaign.end_date,
        'should_consider_history': campaign.should_consider_history,
        'previous_insights': campaign.previous_insights,
        'skills': campaign.skills,
        'skills_for_prompt': campaign.skills_for_prompt(),
    }


def _store_result(campaign: Campaign, api_key: str):
    result = openai_get_campaign_insights(campaign, api_key)
    results[campaign.uuid] = result


@nicer_api.route('/api/v1/campaign/create', methods=['POST'])
def generate_campaign():
    api_key = ProductionConfig.OPENAI_API_KEY
    data = request.get_json()

    if not all(field in data for field in ['name', 'start_date', 'end_date',
                                           'history', 'previous_insights', 'skills']):
        return jsonify({'message': 'Invalid request parameters!'}), 400

    campaign = Campaign(
        name=data['name'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        should_consider_history=data['history'],
        previous_insights=data['previous_insights'],
        skills=data['skills'],
    )

    executor.submit(_store_result, campaign, api_key)

    return jsonify({
        'uuid': campaign.uuid,
        'message': 'Campaign Generated Started',
        'status': 'success'
    })


@nicer_api.route('/api/v1/campaign/get/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    if campaign_id not in results:
        return jsonify({'message': 'Campaign not found!'}), 404

    result = results[campaign_id]
    del results[campaign_id]
    return jsonify(result)


@nicer_api.route('/api/v1/skills/get', methods=['GET'])
def get_skills():
    return jsonify({
        'skills': [
            'Payment Processing',
            'Refunds and Adjustments',
            'Double Booking or Overcharging',
            'Loyalty Program Points or Rewards',
            'Splitting Bills or Group Payments',
            'Check-In and Check-Out',
            'Room Assignments and Upgrades',
            'Reservation Modifications and Cancellations',
            'Lost or Forgotten Items',
            'Room Service and Dining Requests',
            'Hebrew',
            'Arabic',
            'Russian',
            'French',
            'Natural Disasters',
            'Fire Alarms',
            'Medical Emergencies',
            'wi-fi  problems',
            'electronic key card',
            'in-room safe'
        ]
    })

@nicer_api.route('/api/v1/campaing/get_pop/<campaign_id>', methods=['GET'])
def get_pop(campaign_id):
    if campaign_id not in results:
        return jsonify({'message': 'Campaign not found!'}), 404

    result = results[campaign_id]
    return jsonify(result)