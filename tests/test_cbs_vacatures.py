import datetime
import re

import requests
from dateutil.parser import parse

baseUrl = "https://www.cbs.nl/odata/v1"


def test_get_vacancies_should_return_vacancies():
    response = requests.get(baseUrl + "/Vacancies")
    assert_valid_odata_response(response)

    vacancies = response.json()["value"]
    assert len(vacancies) > 1
    assert_valid_vacancies(vacancies)


def test_get_top_vacancies_should_return_number_of_specified_vacancies():
    number_of_vacancies = 2
    response = requests.get(baseUrl + "/Vacancies?$top=%s" % number_of_vacancies)
    assert_valid_odata_response(response)

    vacancies = response.json()["value"]
    assert len(vacancies) == number_of_vacancies
    assert_valid_vacancies(vacancies)


def test_get_skipped_vacancies_should_return_all_but_skipped_vacancies():
    skipped_vacancies = 2
    response_including_skipped = requests.get(baseUrl + "/Vacancies")
    response_excluding_skipped = requests.get(baseUrl + "/Vacancies?$skip=%s" % skipped_vacancies)
    assert_valid_odata_response(response_excluding_skipped)

    vacancies_including_skipped = response_including_skipped.json()["value"]
    vacancies_excluding_skipped = response_excluding_skipped.json()["value"]
    assert_valid_vacancies(vacancies_including_skipped)

    assert len(vacancies_excluding_skipped) == len(vacancies_including_skipped) - skipped_vacancies
    assert vacancies_excluding_skipped[0] == vacancies_including_skipped[skipped_vacancies]
    assert vacancies_excluding_skipped[-1] == vacancies_including_skipped[-1]  # Last vacancy


def test_get_vacancy_by_id_should_return_specified_vacancy():
    response_all = requests.get(baseUrl + "/Vacancies")
    unique_id = response_all.json()["value"][0]["UniqueId"]
    print(response_all.json())
    response = requests.get(baseUrl + "/Vacancies('%s')" % unique_id)
    assert_valid_odata_response(response)

    vacancy = response.json()
    assert vacancy["UniqueId"] == unique_id
    assert vacancy["Title"] == response_all.json()["value"][0]["Title"]
    assert_valid_vacancy(vacancy)


def test_get_nonexistent_vacancy_should_return_not_found():
    nonexistent_id = "00000000-0000-0000-0000-000000000000-nl-nl"
    response = requests.get(baseUrl + "/Vacancies('$%s')" % nonexistent_id)
    assert response.status_code == 204


def test_delete_vacancy_should_return_method_not_allowed():
    nonexistent_id = "00000000-0000-0000-0000-000000000000-nl-nl"
    response = requests.delete(baseUrl + "/Vacancies('$%s')" % nonexistent_id)
    assert response.status_code == 405


def assert_valid_vacancies(vacancies):
    for vacancy in vacancies:
        assert_valid_vacancy(vacancy)


def assert_valid_vacancy(vacancy):
    assert len(vacancy["UniqueId"]) == 42  # <UUID>-nl-nl
    assert len(vacancy["Title"]) > 5
    assert vacancy["MinSalary"] > 500
    assert vacancy["MinSalary"] < 9999
    assert vacancy["MaxSalary"] >= vacancy["MinSalary"]
    assert vacancy["MaxSalary"] < 9999
    assert vacancy["Salary"] == "€ %s tot € %s" % (int(vacancy["MinSalary"]), int(vacancy["MaxSalary"]))
    assert vacancy["SalaryPeriod"] == "MONTH"
    assert len(re.findall("ervaring|niveau", vacancy["YourProfile"])) > 0
    assert "Heerlen" in vacancy["WorkLocation"] or "Den Haag" in vacancy["WorkLocation"]
    assert parse(vacancy["PublicationDate"]).year <= datetime.date.today().year


def assert_valid_odata_response(response):
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert "charset=utf-8" in response.headers["content-type"]
    assert response.headers["odata-version"] == "4.0"
    assert response.json()["@odata.context"].find(baseUrl + "/$metadata#Vacancies") == 0
