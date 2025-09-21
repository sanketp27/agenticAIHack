import re
import json
from datetime import datetime
from jinja2 import Template
from utils.chat_mongo_client import MongoQueryPipelineModule, get_db


class QueryFunctionsModule():
    def __init__(self, query: str, app_name: str, orgId: str):
        self.query = query
        self.app_name = app_name
        self.orgId = orgId
        self.mongo = MongoQueryPipelineModule(orgId)
    
    def _is_average_query(self) -> bool:
        avg_keywords = ["average", "avg", "mean", "typical"]
        query_lower = self.query.lower()
        word_list = query_lower.split()

        for keyword in avg_keywords:
            if keyword in word_list:
                return True
                
        return False
    
    def get_response_data(self, response) -> str:
        res = response.content
        return re.sub(r"```(?:json)?", "", res).strip()

    def get_prompt(self):
        current_date= datetime.now().date().strftime('%d-%b-%Y')
        input_note= f"""
        {"This appears to be a request for an average calculation. Make sure to use the $avg aggregation operator in your query." if self._is_average_query==True else "Generate Query Based on the question."}
        """
        prompt = self.mongo.get_prompt_data(f"{self.app_name}")
        rules = self.mongo.get_prompt_data(f"{self.app_name}_RULES")
        rules =f"Rules: {rules}"
        examples = self.mongo.get_prompt_data(f"{self.app_name}_EXAMPLES")
        prompt = self._get_template(prompt).render(
            input_note= input_note,
            current_date= current_date,
            orgId = self.orgId,
            question= self.query
        )
        
        return prompt, rules, examples
    
    def _get_template(self,data):
        return Template(data)

    def _get_query_response(self, res):
        db = get_db()
        res = json.loads(res)
        
        collection = res["collection"]
        pipeline = res["pipeline"]
        collection = db[collection]
        
        results = collection.aggregate(pipeline)
        res_list = list(results)

        result_array = []
        
        for result in res_list:
            result_array.append(result)
        return result_array
