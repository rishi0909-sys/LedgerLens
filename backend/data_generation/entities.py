from typing import List, Optional
from pydantic import BaseModel
from faker import Faker
import random

class BaseEntity(BaseModel):
    id: str

class Company(BaseEntity):
    name: str
    industry: str
    risk_profile: str

class Employee(BaseEntity):
    name: str
    company_id: str
    role: str
    salary: float

class Vendor(BaseEntity):
    name: str
    category: str
    is_trusted: bool

class Account(BaseEntity):
    entity_id: str
    account_type: str  # 'company', 'employee', 'vendor'
    currency: str
    balance: float

def generate_companies(fake: Faker, count: int) -> List[Company]:
    companies = []
    industries = ['Tech', 'Finance', 'Manufacturing', 'Retail', 'Healthcare']
    risk_profiles = ['low', 'medium', 'high']
    
    for _ in range(count):
        company = Company(
            id=f"COMP_{fake.unique.uuid4()[:8]}",
            name=fake.company(),
            industry=random.choice(industries),
            risk_profile=random.choices(risk_profiles, weights=[0.7, 0.2, 0.1])[0]
        )
        companies.append(company)
    return companies

def generate_employees(fake: Faker, companies: List[Company], count: int) -> List[Employee]:
    employees = []
    roles = ['Manager', 'Developer', 'Sales', 'HR', 'Executive']
    
    for _ in range(count):
        company = random.choice(companies)
        employee = Employee(
            id=f"EMP_{fake.unique.uuid4()[:8]}",
            name=fake.name(),
            company_id=company.id,
            role=random.choice(roles),
            salary=round(random.uniform(40000, 200000), 2)
        )
        employees.append(employee)
    return employees

def generate_vendors(fake: Faker, count: int) -> List[Vendor]:
    vendors = []
    categories = ['IT Services', 'Office Supplies', 'Marketing', 'Legal', 'Consulting']
    
    for _ in range(count):
        vendor = Vendor(
            id=f"VEND_{fake.unique.uuid4()[:8]}",
            name=fake.company() + " " + fake.company_suffix(),
            category=random.choice(categories),
            is_trusted=random.choices([True, False], weights=[0.9, 0.1])[0]
        )
        vendors.append(vendor)
    return vendors

def generate_accounts(fake: Faker, entities: List[BaseEntity], account_type: str) -> List[Account]:
    accounts = []
    for entity in entities:
        # Some entities might have multiple accounts, let's keep it simple with 1-2 for now
        num_accounts = random.choices([1, 2], weights=[0.9, 0.1])[0]
        for _ in range(num_accounts):
            account = Account(
                id=f"ACC_{fake.unique.uuid4()[:8]}",
                entity_id=entity.id,
                account_type=account_type,
                currency="USD",
                balance=round(random.uniform(1000, 100000), 2)
            )
            accounts.append(account)
    return accounts
