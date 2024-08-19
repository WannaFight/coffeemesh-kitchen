import datetime
import uuid
from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint

blueprint = Blueprint("kitchen", __name__, description="Kitchen API")

schedules = [
    {
        "id": uuid.uuid4(),
        "scheduled": datetime.datetime.now(),
        "status": "pending",
        "order": [
            {
                "product": "capuccino",
                "quantity": 1,
                "size": "big",
            },
        ],
    }
]


@blueprint.route("/kitchen/schedules")
class KitchenSchedules(MethodView):
    def get(self):
        return {"schedules": schedules}, HTTPStatus.OK

    def post(self, payload):
        return schedules[0], HTTPStatus.CREATED


@blueprint.route("/kitchen/schedules/<schedule_id>")
class KitchenSchedule(MethodView):
    def get(self, schedule_id):
        return schedules[0], HTTPStatus.OK

    def put(self, payload, schedule_id):
        return schedules[0], HTTPStatus.OK

    def delete(self, schedule_id):
        return "", HTTPStatus.NO_CONTENT


@blueprint.route("/kitchen/schedules/<schedule_id>/cancel", methods=["POST"])
def cancel_schedule(schedule_id):
    return schedules[0], HTTPStatus.OK


@blueprint.route("/kitchen/schedules/<schedule_id>/status", methods=["GET"])
def get_schedule_status(schedule_id):
    return schedules[0], HTTPStatus.OK
