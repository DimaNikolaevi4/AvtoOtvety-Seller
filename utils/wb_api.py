import requests

def get_wb_feedbacks(api_key):
    """
    Получает список отзывов с Wildberries и приводит к единому формату.
    Возвращает список словарей с полями:
    - id
    - text
    - rating (целое число 1–5)
    - created_at (строка с датой)
    - is_answered (bool)
    - product_name (название товара)
    """
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
    
    headers = {
        "Authorization": api_key
    }
    
    params = {
        "isAnswered": False,
        "take": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        feedbacks = data.get("feedbacks", [])
        result = []
        for item in feedbacks:
            # У Wildberries оценка хранится в поле productRating (может быть целым или float)
            rating = item.get("productRating", 0)
            # Приводим к int, если нужно
            if isinstance(rating, float):
                rating = int(rating)
            
            result.append({
                "id": item.get("id"),
                "text": item.get("text", ""),
                "rating": rating,
                "created_at": item.get("createdDate", ""),
                "is_answered": item.get("answered", False),
                "product_name": item.get("product", {}).get("name", "")
            })
        return result
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Wildberries: {e}")
        return None