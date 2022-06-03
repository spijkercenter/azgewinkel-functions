import os
from typing import List, Dict, TypeVar

from flask import render_template
from requests import Request

from client import AZGewinkelClient
from models.customer import Customer
from models.line_item import LineItem
from models.order import Order
from models.order_status import OrderStatus

K = TypeVar("K")
V = TypeVar("V")


def main(request: Request = None) -> str:
    self_url = os.environ.get("SELF_URL", "http://localhost:8080/")

    orders = _load_orders()
    grouped_orders = _group_orders_by_customer(orders)
    grouped_orders = _filter_on_customer(request.url, grouped_orders)

    grouped_line_items = _group_line_items_by_status(grouped_orders)

    return render_template('orders.html',
                           all_statuses=OrderStatus.all(),
                           orders_by_customer=grouped_orders,
                           line_items_by_status=grouped_line_items,
                           linkable=len(grouped_orders) != 1,
                           url=self_url,
                           )


def _load_orders() -> List[Order]:
    client = AZGewinkelClient()
    customers = client.load("/customers", Customer.of)
    orders = client.load("/orders", lambda raw: Order.of(raw, customers))
    orders = [o for o in orders.values() if o.status.key != "completed" and o.status != "refunded"]
    orders.sort()
    return orders


def _group_orders_by_customer(orders: List[Order]) -> Dict[Customer, List[Order]]:
    result = {}

    # Group
    for order in orders:
        customer = order.customer
        if customer in result:
            o = result[customer]
        else:
            o = []
        o.append(order)
        result[order.customer] = o

    # Sort
    return _sort_dict(result)


def _group_line_items_by_status(orders: Dict[Customer, List[Order]]) -> Dict[OrderStatus, List[LineItem]]:
    line_items_by_status: Dict[OrderStatus, Dict[str, int]] = {}
    for orders in orders.values():
        for order in orders:
            status = order.status
            if status in line_items_by_status:
                line_items = line_items_by_status[status]
            else:
                line_items = {}

            for line_item in order.line_items:
                name = line_item.name
                if name in line_items:
                    q = line_items[name] + line_item.quantity
                else:
                    q = line_item.quantity
                line_items[name] = q
            line_items_by_status[status] = line_items

    result: Dict[OrderStatus, List[LineItem]] = {}
    for k in sorted(line_items_by_status):
        result[k] = sorted([LineItem(n, q) for n, q in line_items_by_status[k].items()])
    return result


def _filter_on_customer(url: str, orders: Dict[Customer, List[Order]]) -> Dict[Customer, List[Order]]:
    cust_filter = url.split("/")[-1]
    filtered_customers = [c for c in orders.keys() if c.shortname == cust_filter]
    if filtered_customers:
        return {filtered_customers[0]: orders[filtered_customers[0]]}
    else:
        return orders


def _sort_dict(d: Dict[K, V]) -> Dict[K, V]:
    s = {}
    for k in sorted(d):
        s[k] = d[k]
    return s


if __name__ == '__main__':
    print(main())
