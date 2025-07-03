import requests

class Price:
    def __init__(self, is_reduction, current_price, original_price=None, reduction_percentage=None):
        self.is_reduction = is_reduction
        self.current_price = current_price
        self.original_price = original_price
        self.reduction_percentage = reduction_percentage

    def __repr__(self):
        return (
            f"Price(is_reduction={self.is_reduction}, "
            f"current_price='{self.current_price}', "
            f"original_price='{self.original_price}', "
            f"reduction_percentage='{self.reduction_percentage}')"
        )
    
    def to_dict(self):
        return {
            "is_reduction": self.is_reduction,
            "current_price": self.current_price,
            "original_price": self.original_price,
            "reduction_percentage": self.reduction_percentage
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            is_reduction=data.get("is_reduction"),
            current_price=data.get("current_price"),
            original_price=data.get("original_price"),
            reduction_percentage=data.get("reduction_percentage")
        )

class SteamSales:
    def search(self, appid: str) -> Price:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=fr&l=french"
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            raise Exception("Erreur lors de la requête")

        data = response.json()
        if not data[str(appid)]["success"]:
            raise Exception("AppID invalide ou non disponible")

        price_info = data[str(appid)]["data"].get("price_overview")
        if price_info:
            final_price = price_info["final"] / 100
            initial_price = price_info["initial"] / 100
            discount_percent = price_info["discount_percent"]

            is_reduction = discount_percent > 0
            current_price = final_price
            original_price = initial_price if is_reduction else None
            reduction_percentage = f"{discount_percent}%" if is_reduction else None

            return Price(
                is_reduction=is_reduction,
                current_price=current_price,
                original_price=original_price,
                reduction_percentage=reduction_percentage
            )
        else:
            return Price(
                is_reduction=False,
                current_price="Gratuit"
            )
