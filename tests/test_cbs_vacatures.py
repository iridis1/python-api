import requests

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


def test_get_nonexistent_vacancy_should_return_not_found():
    nonexistent_id = "00000000-0000-0000-0000-000000000000-nl-nl"
    response = requests.get(baseUrl + "/Vacancies('$%s')" % nonexistent_id)
    assert response.status_code == 204


def assert_valid_vacancies(vacancies):
    for vacancy in vacancies:
        assert_valid_vacancy(vacancy)


def assert_valid_vacancy(vacancy):
    assert "Title" in vacancy
    assert len(vacancy["Title"]) > 5
    assert len(vacancy["UniqueId"]) == 42  # <UUID>-nl-nl
    assert vacancy["MinSalary"] > 500
    assert vacancy["MinSalary"] < 9999
    assert vacancy["MaxSalary"] >= vacancy["MinSalary"]
    assert vacancy["MaxSalary"] < 9999
    assert vacancy["SalaryPeriod"] == "MONTH"


def assert_valid_odata_response(response):
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert "charset=utf-8" in response.headers["content-type"]
    assert response.headers["odata-version"] == "4.0"
    assert response.json()["@odata.context"].find(baseUrl + "/$metadata#Vacancies") == 0
