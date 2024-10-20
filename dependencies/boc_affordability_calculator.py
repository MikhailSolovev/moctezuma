import requests

url = "https://www.bankofcyprus.com/ajax/AffordabilityCalculatorBlock/GetResult"

class Person:
    def __init__(
        self,
        age,
        duration_in_months,
        installment_amount,
        monthly_expenses,
        net_monthly_salary,
        # home loan = 1
        product_id,
        # first home = 101, holiday home = 102
        purpose_id,
    ):
        self.age = age
        self.duration_in_months = duration_in_months
        self.installment_amount = installment_amount
        self.monthly_expenses = monthly_expenses
        self.net_monthly_salary = net_monthly_salary
        self.product_id = product_id
        self.purpose_id = purpose_id

class AffordabilityCalculatorClient:
    @classmethod
    def calculate_affordability(cls, person: Person) -> float:
        resp = requests.post(url, json={
            "age": person.age,
            "durationInMonths": person.duration_in_months,
            "installmentAmount": person.installment_amount,
            "monthlyExpenses": person.monthly_expenses,
            "netMonthlySalary": person.net_monthly_salary,
            "productId": person.product_id,
            "purposeId": person.purpose_id,
        })

        if resp.text == '':
            return -1

        return resp.json()["finalCalculationWebList"][0]["objectValue"]

# Example of usage
# AffordabilityCalculatorClient.calculate_affordability(Person(
#     age=44,
#     duration_in_months=178,
#     installment_amount=3000,
#     monthly_expenses=2000,
#     net_monthly_salary=30000,
#     product_id=1,
#     purpose_id=101,
# ))