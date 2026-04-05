import requests

class YandexAPI:
    def __init__(self, oauth_token):
        self.oauth_token = oauth_token
        self.base_url = "https://api.partner.market.yandex.ru"

    def _headers(self):
        return {
            "Authorization": f"OAuth {self.oauth_token}",
            "Content-Type": "application/json"
        }

    def get_feedbacks(self, limit=50, offset=0, from_date=None):
        """
        Получить отзывы о магазине.
        Документация: https://yandex.ru/dev/market/partner-api/doc/ru/reference/feedback/get-feedback
        """
        url = f"{self.base_url}/v2/feedback"
        params = {
            "limit": limit,
            "offset": offset
        }
        if from_date:
            params["from"] = from_date  # дата в формате ISO 8601
        
        try:
            response = requests.get(url, headers=self._headers(), params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Структура ответа: {"feedbacks": [...]}
            result = []
            for item in data.get("feedbacks", []):
                result.append({
                    "id": item.get("id"),
                    "text": item.get("text", ""),
                    "rating": item.get("grade", 0),   # оценка 1-5
                    "created_at": item.get("createdAt"),
                    "is_answered": item.get("answer") is not None,
                    "product_name": item.get("product", {}).get("name", ""),
                    "shop_id": item.get("shopId")
                })
            return result
        except requests.exceptions.RequestException as e:
            print(f"Yandex API error: {e}")
            raise

    def answer_feedback(self, feedback_id, text):
        """
        Ответить на отзыв.
        Документация: https://yandex.ru/dev/market/partner-api/doc/ru/reference/feedback/put-feedback-answer
        """
        url = f"{self.base_url}/v2/feedback/{feedback_id}/answer"
        payload = {
            "text": text
        }
        response = requests.put(url, headers=self._headers(), json=payload, timeout=10)
        response.raise_for_status()
        return response.json()