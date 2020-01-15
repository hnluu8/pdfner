import pytest


def pytest_addoption(parser):
    parser.addoption("--pdf_file", action="store", default="./data/gre_research_validity_data.pdf")
    parser.addoption("--corenlp_server_home", action="store", default="./tools/stanford-corenlp-full-2018-10-05")


@pytest.fixture
def pdf_file(request):
    return request.config.getoption('--pdf_file')

@pytest.fixture
def corenlp_server_home(request):
    return request.config.getoption('--corenlp_server_home')
