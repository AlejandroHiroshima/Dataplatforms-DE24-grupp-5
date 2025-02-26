from requests import Session
import requests  

def get_exchange_rates(base_currency="USD", rate ="SEK"):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    
    with Session() as session:
    
        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()       
            return data["rates"][rate] #vad som returneras
        except requests.exceptions.RequestException as e:
            print(f"Failed to obtain exchange rate: {e}")
            return None
    
if __name__ == "__main__":
    get_exchange_rates("USD") 