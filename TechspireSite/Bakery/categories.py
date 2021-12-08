from . import models as m


class SubApp:
    app_url = ""
    app_label = "Test"
    models = []


class Primary(SubApp):
    app_label = "Primary"
    models = [m.Order, m.Customer, m.Employee]


class Secondary(SubApp):
    app_label = "Secondary"
    models = [m.PointReason, m.ProductType, m.CustomerStatus]
