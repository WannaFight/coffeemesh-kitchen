import copy
import datetime
import uuid
from http import HTTPStatus

from flask import abort
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import ValidationError

from api.schemas import (
    GetKitchenScheduleParameters,
    GetScheduledOrderSchema,
    GetScheduledOrdersSchema,
    ScheduleOrderSchema,
    ScheduleStatusSchema,
)

blueprint = Blueprint("kitchen", __name__, description="Kitchen API")

schedules = []


def validate_schedule(schedule):
    schedule = copy.deepcopy(schedule)
    schedule["scheduled"] = schedule["scheduled"].isoformat()
    errors = GetScheduledOrderSchema().validate(schedule)
    if errors:
        raise ValidationError(errors)


@blueprint.route("/kitchen/schedules")
class KitchenSchedules(MethodView):
    @blueprint.arguments(GetKitchenScheduleParameters, location="query")
    @blueprint.response(status_code=HTTPStatus.OK, schema=GetScheduledOrdersSchema)
    def get(self, parameters):
        for schedule in schedules:
            validate_schedule(schedule)

        if not parameters:
            return {"schedules": schedules}

        queryset = [schedule for schedule in schedules]

        if (in_progress := parameters.get("progress")) is not None:
            if in_progress:
                queryset = [
                    schedule
                    for schedule in queryset
                    if schedule["status"] == "progress"
                ]
            else:
                queryset = [
                    schedule
                    for schedule in queryset
                    if schedule["status"] != "progress"
                ]

        if (since := parameters.get("since")) is not None:
            since = since.replace(tzinfo=datetime.timezone.utc)
            queryset = [
                schedule for schedule in queryset if schedule["scheduled"] >= since
            ]

        if (limit := parameters.get("limit")) is not None and len(queryset) > limit:
            queryset = queryset[:limit]

        return {"schedules": queryset}

    @blueprint.arguments(ScheduleOrderSchema)
    @blueprint.response(status_code=HTTPStatus.CREATED, schema=GetScheduledOrderSchema)
    def post(self, payload):
        payload["id"] = str(uuid.uuid4())
        payload["scheduled"] = datetime.datetime.now(tz=datetime.timezone.utc)
        payload["status"] = "pending"

        validate_schedule(payload)
        schedules.append(payload)

        return payload


@blueprint.route("/kitchen/schedules/<schedule_id>")
class KitchenSchedule(MethodView):
    @blueprint.response(status_code=HTTPStatus.OK, schema=GetScheduledOrderSchema)
    def get(self, schedule_id):
        for schedule in schedules:
            if schedule["id"] == schedule_id:
                validate_schedule(schedule)
                return schedule
        abort(
            HTTPStatus.NOT_FOUND,
            description=f"Resource with ID={schedule_id} not found",
        )

    @blueprint.arguments(schema=ScheduleOrderSchema)
    @blueprint.response(status_code=HTTPStatus.OK, schema=GetScheduledOrderSchema)
    def put(self, payload, schedule_id):
        for schedule in schedules:
            if schedule["id"] == schedule_id:
                schedule.update(payload)
                validate_schedule(schedule)
                return schedule
        abort(
            HTTPStatus.NOT_FOUND,
            description=f"Resource with ID={schedule_id} not found",
        )

    @blueprint.response(status_code=HTTPStatus.NO_CONTENT)
    def delete(self, schedule_id):
        for idx, schedule in enumerate(schedules):
            if schedule["id"] == schedule_id:
                schedules.pop(idx)
                return None
        abort(
            HTTPStatus.NOT_FOUND,
            description=f"Resource with ID={schedule_id} not found",
        )


@blueprint.response(status_code=HTTPStatus.OK, schema=GetScheduledOrderSchema)
@blueprint.route("/kitchen/schedules/<schedule_id>/cancel", methods=["POST"])
def cancel_schedule(schedule_id):
    for schedule in schedules:
        if schedule["id"] == schedule_id:
            schedule["status"] = "cancelled"
            validate_schedule(schedule)
            return schedule
    abort(
        HTTPStatus.NOT_FOUND,
        description=f"Resource with ID={schedule_id} not found",
    )


@blueprint.response(status_code=HTTPStatus.OK, schema=ScheduleStatusSchema)
@blueprint.route("/kitchen/schedules/<schedule_id>/status", methods=["GET"])
def get_schedule_status(schedule_id):
    for schedule in schedules:
        if schedule["id"] == schedule_id:
            validate_schedule(schedule)
            return {"status": schedule["status"]}
    abort(
        HTTPStatus.NOT_FOUND,
        description=f"Resource with ID={schedule_id} not found",
    )
