import logging
import yaml

from binance.client import Client

logging.basicConfig(format='%(asctime)s - (%(threadName)-10s) - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
LOG = logging.getLogger(__name__)


api = None
with open("src/key.yaml", 'r') as stream:
    try:
        api = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise Exception("Can not load key/secret")


client = Client(api['k'], api['s'])

LOG.info("Account info...")
status = client.get_account_status()
LOG.info(status)

LOG.info("Account balance...")
prices = { p['symbol']: p['price'] for p in client.get_all_tickers() if p['symbol'].endswith('USDT') or p['symbol'].endswith('BTC') }

balances = { b['asset']: b for b in client.get_account()["balances"] if float(b["free"]) > .5 or float(b["locked"]) > .5}
acc_info = ""
total_value = 0.0
for a in balances.values():
    price = float(prices[a['asset']+"USDT"]) if a['asset'] != 'USDT' else 1.0
    free = float(a['free'])
    locked = float(a['locked'])
    amount = free + locked
    value = price * amount
    if value <= 10.0:
        continue
    total_value = total_value + value
    acc_info = acc_info + f"Coin {a['asset']}\n\tstill free: {free:9.2f}\n\tin order: {locked:9.2f}\n\tprice: {price:9.2f} USDT\n\tcost: {value:9.2f} USDT\n"
LOG.info(f"\nTotal: {total_value:9.2f} USDT\n{acc_info}")

LOG.info("Check orders...")
order_info = "\n"
for b in sorted(balances.keys()):
    for o in client.get_open_orders():
        if not o['symbol'].startswith(b):
            continue
        unit = o['symbol'].replace(b, '')
        qty = float(o['origQty'])
        price = float(o['price'])
        value = qty * price
        order_info = order_info + f"Order {o['symbol']} ({o['status']}): ID: {o['orderId']} - {o['type']} - {value:9.2f} {unit} Qty. {qty:9.2f} Price {price:9.2f} {unit}\n"
LOG.info(f"{order_info}")
