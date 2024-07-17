import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from requests_html import HTMLSession
from pprint import pprint
import json
import re


def gen_headers():
    headers = Headers(browser='chrome', os='win')
    return headers.generate()


response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=gen_headers())
html_data = response.text
soup = BeautifulSoup(html_data, 'html.parser')
vacancy_list = soup.find_all('div', class_="vacancy-search-item__card")
vacancies = []
for vacancy in vacancy_list:
    a_tag = vacancy.find('a', class_='bloko-link')
    company_tag = vacancy.find('a', class_='bloko-link bloko-link_kind-secondary')
    city_tag = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
    salary_tag = vacancy.find('span', class_='fake-magritte-primary-text--Hdw8FvkOzzOcoR4xXWni')

    link = a_tag['href']
    company = company_tag.text.strip()
    city = city_tag.text.strip()
    salary = salary_tag.text
    if salary in ['Москва', 'Санкт-Петербург']:
        salary = 'Не указана'
    if salary is not None:
        pattern = re.compile(r'\u202f')
        repl = ' '
        salary = re.sub(pattern, repl, salary)

    session = HTMLSession()
    response = session.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    vacancy_tag = soup.find('div', {'data-qa': 'vacancy-description'})
    vacancy_text = vacancy_tag.text
    # print(vacancy_text)
    searchwords_1 = 'Flask'
    searchwords_2 = 'Django'
    if searchwords_1.lower() or searchwords_2.lower() in vacancy_text.lower():
        result = {
            'ссылка': link,
            'компания': company.replace('\xa0', ' '),
            'город': city,
            'зарплата': salary.replace('\xa0', ' ')
        }
        vacancies.append(result)
pprint(vacancies)

with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(vacancies, file, ensure_ascii=False, indent=4)


