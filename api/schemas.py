from marshmallow import EXCLUDE, Schema, fields, validate


class OrderItemSchema(Schema):
    product = fields.String(required=True)
    size = fields.String(
        required=True, validate=validate.OneOf(["small", "medium", "big"])
    )
    quantity = fields.Integer(
        validate=validate.Range(1, 1_000_000, min_inclusive=True, max_inclusive=True),
        required=True,
    )

    class Meta:
        unknown = EXCLUDE


class ScheduleOrderSchema(Schema):
    order = fields.List(fields.Nested(OrderItemSchema), required=True)

    class Meta:
        unknown = EXCLUDE


class GetScheduledOrderSchema(ScheduleOrderSchema):
    id = fields.UUID(required=True)
    scheduled = fields.DateTime(required=True)
    status = fields.String(
        required=True,
        validate=validate.OneOf(["pending", "progress", "cancelled", "finished"]),
    )


class GetScheduledOrdersSchema(Schema):
    schedules = fields.List(fields.Nested(GetScheduledOrderSchema), required=True)

    class Meta:
        unknown = EXCLUDE


class ScheduleStatusSchema(Schema):
    status = fields.String(
        required=True,
        validate=validate.OneOf(["pending", "progress", "cancelled", "finished"]),
    )


class GetKitchenScheduleParameters(Schema):
    progress = fields.Boolean()
    limit = fields.Integer()
    since = fields.DateTime()

    class Meta:
        unknown = EXCLUDE
