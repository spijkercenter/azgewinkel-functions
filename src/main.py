import os

from flask import render_template
from requests import Request

from client import AZGewinkelClient
from models.customer import Customer
from models.order import Order, order_stati


def main(request: Request = None) -> str:
    self_url = os.environ.get("SELF_URL", "localhost:8080/")
    client = AZGewinkelClient()
    customers = client.load("/customers", Customer.of)
    orders = client.load("/orders", lambda raw: Order.of(raw, customers))
    orders = [o for o in orders.values() if o.status != "completed" and o.status != "refunded"]
    orders.sort()

    orders_by_customer = {}

    for order in orders:
        customer = order.customer
        if customer in orders_by_customer:
            o = orders_by_customer[customer]
        else:
            o = []
        o.append(order)
        orders_by_customer[order.customer] = o

    cust_filter = None
    linkable = True
    if request:
        cust_filter = request.url.split("/")[-1]
    filtered_customers = [c for c in orders_by_customer.keys() if c.shortname == cust_filter]
    if filtered_customers:
        orders_by_customer = {filtered_customers[0]: orders_by_customer[filtered_customers[0]]}
        linkable = False

    return render_template('orders.html',
                           orders_by_customer=orders_by_customer,
                           linkable=linkable,
                           order_stati=order_stati,
                           url=self_url,
                           )


if __name__ == '__main__':
    print(main())
