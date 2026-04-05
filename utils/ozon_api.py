import requests

class OzonAPI:
    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = "https://api-seller.ozon.ru"

    def _headers(self):
        return {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def get_feedbacks(self, limit=50, offset=0):
        """
        Получить список отзывов.
        Возвращает список словарей с полями:
        - id
        - text (текст отзыва)
        - rating (оценка 1-5)
        - created_at
        - is_answered (отвечено ли)
        - product_name (название товара)
        """
        url = f"{self.base_url}/v1/feedback/list"
        payload = {
            "filter": {
                "answered": False   # можно получать только неотвеченные
            },
            "limit": limit,
            "offset": offset
        }
        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Преобразуем в удобный формат
            result = []
            for item in data.get("result", []):
                result.append({
                    "id": item["id"],
                    "text": item.get("text", ""),
                    "rating": item.get("rating", 0),
                    "created_at": item.get("created_at"),
                    "is_answered": item.get("answered", False),
                    "product_name": item.get("product", {}).get("name", "")
                })
            return result
        except requests.exceptions.RequestException as e:
            print(f"Ozon API error: {e}")
            raise

    def answer_feedback(self, feedback_id, text):
        """
        Отправить ответ на отзыв.
        """
        url = f"{self.base_url}/v1/feedback/answer"
        payload = {
            "feedback_id": feedback_id,
            "text": text
        }
        response = requests.post(url, headers=self._headers(), json=payload, timeout=10)
        response.raise_for_status()
        return response.json()