# Binance Manual Trade

## Install
```
apt-get update 

# install Python >=3.8.2
yes | pip3 install --upgrade setuptools
yes | pip3 install -r ./requirements.txt

```

## API-KEY
fill the API key, secret into the key.yaml file
```
k: <binance_api_key>
s: <binance_api_secret>
```

### Run
```
# account and order view
python3 src/account.py

# place/ cancel/ view order(s)
python3 src/order.py -h
```